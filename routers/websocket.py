import asyncio
import json

import boto3
from amazon_transcribe.client import TranscribeStreamingClient
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from model.WebsocketEventHandler import WebSocketEventHandler
from datetime import datetime


router = APIRouter()

@router.websocket("/transcribe")
async def websocket_transcript_endpoint(websocket: WebSocket):

    SAMPLE_RATE = 16000
    REGION = "us-east-1"
    S3_BUCKET = "cc-audio-save"

    await websocket.accept()

    websocket_closed = False
    stream = None
    session_transcripts = []  # 세션별 텍스트 저장
    current_session_active = False
    audio_buffer = []  # 전체 웹소켓 세션 동안의 음성 데이터 저장
    session_start_time = datetime.now()

    try:
        # AWS Transcribe 클라이언트 설정
        client = TranscribeStreamingClient(region=REGION)

        async def upload_audio_to_s3():
            nonlocal audio_buffer, session_start_time

            if not audio_buffer:
                print("업로드할 음성 데이터가 없습니다.")
                return None

            try:
                s3_client = boto3.client('s3', region_name=REGION)

                timestamp = session_start_time.strftime("%Y%m%d_%H%M%S")
                filename = f"audio_session_{timestamp}.wav"

                # 음성 데이터 결합
                audio_data = b''.join(audio_buffer)


                # WAV 헤더 생성 (16-bit PCM, 16kHz, 모노)
                wav_header = create_wav_header(len(audio_data), SAMPLE_RATE, 1, 16)
                wav_data = wav_header + audio_data

                # S3 업로드
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=filename,
                    Body=wav_data,
                    ContentType='audio/wav',
                    Metadata={
                        'session_start': session_start_time.isoformat(),
                        'duration_seconds': str(len(audio_data) // (SAMPLE_RATE * 2)),
                        'sample_rate': str(SAMPLE_RATE),
                        'channels': '1',
                        'bit_depth': '16'
                    }
                )

                print(f"음성 파일이 S3에 업로드되었습니다: s3://{S3_BUCKET}/{filename}")
                return f"s3://{S3_BUCKET}/{filename}"

            except Exception as e:
                print(f"S3 업로드 중 오류 발생: {e}")
                return None

        def create_wav_header(data_length, sample_rate, channels, bits_per_sample):
            import struct

            # WAV 헤더 구조 (더 정확한 계산)
            chunk_id = b'RIFF'
            chunk_size = 36 + data_length  # 전체 파일 크기 - 8
            format_type = b'WAVE'
            subchunk1_id = b'fmt '
            subchunk1_size = 16
            audio_format = 1  # PCM
            num_channels = channels
            byte_rate = sample_rate * channels * bits_per_sample // 8
            block_align = channels * bits_per_sample // 8
            subchunk2_id = b'data'
            subchunk2_size = data_length

            # 리틀 엔디안으로 패킹
            header = struct.pack('<4sI4s4sIHHIIHH4sI',
                                 chunk_id, chunk_size, format_type,
                                 subchunk1_id, subchunk1_size, audio_format,
                                 num_channels, sample_rate, byte_rate,
                                 block_align, bits_per_sample,
                                 subchunk2_id, subchunk2_size)

            return header


        # 새로운 세션 시작 함수
        async def start_new_session():
            nonlocal stream, current_session_active, session_transcripts

            # 새 세션 초기화
            session_transcripts = []
            current_session_active = True

            # 새로운 음성 인식 스트림 시작
            stream = await client.start_stream_transcription(
                language_code="ko-KR",
                media_sample_rate_hz=SAMPLE_RATE,
                media_encoding="pcm",
            )

            # 새로운 핸들러로 이벤트 처리 시작
            handler = WebSocketEventHandler(stream.output_stream, websocket,
                                             websocket_closed, session_transcripts, current_session_active)
            asyncio.create_task(handler.handle_events())

            print("새로운 음성 인식 세션이 시작되었습니다.")

        # WebSocket에서 데이터를 받아서 처리하는 함수
        async def process_websocket_data():
            nonlocal websocket_closed, current_session_active, session_transcripts

            try:
                while not websocket_closed:
                    # WebSocket에서 데이터 수신
                    try:
                        data = await websocket.receive()
                    except WebSocketDisconnect:
                        print("WebSocket 연결이 끊어졌습니다.")
                        break

                    if websocket_closed:
                        break

                    # JSON 데이터인지 확인 (stop 신호)
                    if 'text' in data:
                        try:
                            json_data = json.loads(data['text'])
                            if json_data.get('type') == 'stop':
                                print("=== 세션 정지 신호 받음 ===")
                                current_session_active = False

                                # 세션의 모든 STT 결과 출력
                                print("=== 세션 STT 결과 ===")
                                if session_transcripts:
                                    full_transcript = " ".join(session_transcripts)
                                    print(f"전체 텍스트: {full_transcript}")
                                    print(f"총 문장 수: {len(session_transcripts)}")
                                    for i, text in enumerate(session_transcripts, 1):
                                        print(f"{i}. {text}")
                                else:
                                    print("인식된 텍스트가 없습니다.")
                                print("===================")

                                # WebSocket으로 세션 완료 알림
                                await websocket.send_json({
                                    "type": "session_complete",
                                    "full_transcript": " ".join(session_transcripts) if session_transcripts else "",
                                    "sentence_count": len(session_transcripts)
                                })

                                continue
                            elif json_data.get('type') == 'end':
                                print("=== 세션 종료 신호 받음 ===")
                                current_session_active = False

                                # 스트림 종료
                                if stream and stream.input_stream:
                                    try:
                                        await stream.input_stream.end_stream()
                                        # 잠시 대기하여 마지막 결과 처리
                                        await asyncio.sleep(1)
                                    except Exception as e:
                                        print(f"스트림 종료 중 오류: {e}")

                                # S3에 음성 파일 업로드
                                s3_url = await upload_audio_to_s3()
                                if s3_url:
                                    await websocket.send_json({
                                        "type": "audio_uploaded",
                                        "s3_url": s3_url
                                    })

                                continue

                        except json.JSONDecodeError:
                            pass  # JSON이 아닌 경우 오디오 데이터로 처리

                    # 바이너리 데이터인 경우 (오디오 데이터)
                    if 'bytes' in data:
                        audio_data = data['bytes']
                        audio_buffer.append(audio_data)

                        # 세션이 활성화되지 않았다면 새로운 세션 시작
                        if not current_session_active:
                            await start_new_session()

                        # 받은 오디오 데이터를 AWS Transcribe 스트림으로 전송
                        if stream and stream.input_stream and current_session_active:
                            try:
                                await stream.input_stream.send_audio_event(audio_chunk=audio_data)
                            except Exception as e:
                                print(f"오디오 전송 중 오류: {e}")
                                current_session_active = False
                print("WebSocket 연결이 닫혔습니다.")

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}")
                websocket_closed = True

        # 데이터 처리 시작
        await process_websocket_data()

    except WebSocketDisconnect:
        print("WebSocket이 이미 연결 해제되었습니다.")
        websocket_closed = True
    except Exception as e:
        print(f"WebSocket 처리 중 오류 발생: {e}")
        if not websocket_closed:
            try:
                await websocket.send_json({"error": str(e)})
            except:
                websocket_closed = True
    finally:
        # WebSocket이 아직 열려있을 때만 닫기
        if not websocket_closed:
            try:
                await websocket.close()
            except Exception as e:
                print(f"WebSocket 종료 중 오류: {e}")
        print("WebSocket 연결이 종료되었습니다.")
