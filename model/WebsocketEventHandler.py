# WebSocket 이벤트 핸들러 정의
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent


class WebSocketEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, websocket, websocket_closed, session_transcripts, current_session_active):
        super().__init__(output_stream)
        self.websocket = websocket
        self.websocket_closed = websocket_closed
        self.session_transcripts = session_transcripts
        self.current_session_active = current_session_active


    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        if self.websocket_closed or not self.current_session_active:
            return

        try:
            results = transcript_event.transcript.results
            for result in results:
                for alt in result.alternatives:
                    # 실시간으로 인식된 텍스트를 WebSocket으로 전송
                    transcript_data = {
                        "transcript": alt.transcript,
                        "is_partial": result.is_partial,
                        "confidence": getattr(alt, 'confidence', None)
                    }
                    await self.websocket.send_json(transcript_data)

                    # 완료된 텍스트만 세션에 저장 (부분 결과가 아닌 경우)
                    if not result.is_partial and alt.transcript.strip():
                        self.session_transcripts.append(alt.transcript.strip())

        except Exception as e:
            print(f"텍스트 전송 중 오류: {e}")
            websocket_closed = True