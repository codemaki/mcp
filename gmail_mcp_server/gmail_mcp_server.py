import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']

import os

# 환경변수에서 포트 가져오기 (기본값: 11011)
port = int(os.getenv("PORT", 11011))
host = os.getenv("HOST", "0.0.0.0")

# 기본 리다이렉트 URI (환경변수로 오버라이드 가능)
DEFAULT_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "https://skax.app/oauth/callback")

mcp = FastMCP("Gmail MCP Server", host=host, port=port)

class GmailService:
    def __init__(self):
        self.service = None
        self.credentials = None

    def authenticate(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        """Gmail API 인증을 처리합니다."""
        creds = None

        # 스크립트와 같은 디렉토리 기준으로 절대경로 생성
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(credentials_path):
            credentials_path = os.path.join(script_dir, credentials_path)
        if not os.path.isabs(token_path):
            token_path = os.path.join(script_dir, token_path)

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=8080, open_browser=True)

            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def get_messages(self, query: str = "", max_results: int = 10) -> List[Dict]:
        """Gmail 메시지를 조회합니다."""
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            detailed_messages = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()

                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')

                body = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                break
                else:
                    if msg['payload']['mimeType'] == 'text/plain':
                        if 'data' in msg['payload']['body']:
                            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

                detailed_messages.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': msg.get('snippet', ''),
                    'body': body[:500] + "..." if len(body) > 500 else body
                })

            return detailed_messages

        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")

    def send_message(self, to: str, subject: str, body: str, html_body: str = None) -> Dict:
        """Gmail로 메시지를 발송합니다."""
        try:
            if html_body:
                message = MIMEMultipart('alternative')
                text_part = MIMEText(body, 'plain')
                html_part = MIMEText(html_body, 'html')
                message.attach(text_part)
                message.attach(html_part)
            else:
                message = MIMEText(body)

            message['to'] = to
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {
                'id': send_message['id'],
                'status': 'sent',
                'message': f'Email sent successfully to {to}'
            }

        except HttpError as error:
            raise Exception(f"Failed to send email: {error}")

# Gmail 서비스 인스턴스
gmail_service = GmailService()

@mcp.tool()
def gmail_authenticate(credentials_path: str = "credentials.json", token_path: str = "token.json") -> str:
    """Gmail API 인증을 수행합니다.

    Args:
        credentials_path: OAuth2 클라이언트 자격 증명 파일 경로
        token_path: 액세스 토큰을 저장할 파일 경로
    """
    try:
        gmail_service.authenticate(credentials_path, token_path)
        return "Gmail 인증이 성공적으로 완료되었습니다."
    except Exception as e:
        return f"Gmail 인증 실패: {str(e)}"

@mcp.tool()
def gmail_authenticate_with_refresh_token(refresh_token: str, client_id: str, client_secret: str) -> str:
    """Refresh Token을 사용하여 Gmail API 인증을 수행합니다.

    Args:
        refresh_token: Google OAuth2 Refresh Token
        client_id: OAuth2 클라이언트 ID
        client_secret: OAuth2 클라이언트 시크릿
    """
    try:
        from google.oauth2.credentials import Credentials

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )

        # 토큰 갱신
        creds.refresh(Request())

        gmail_service.credentials = creds
        gmail_service.service = build('gmail', 'v1', credentials=creds)

        # 토큰 파일 저장 (선택사항)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(script_dir, "token.json")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

        return "Gmail 인증이 성공적으로 완료되었습니다."
    except Exception as e:
        return f"Gmail 인증 실패: {str(e)}"

@mcp.tool()
def get_refresh_token_from_auth_code(auth_code: str, client_id: str, client_secret: str, redirect_uri: str = None) -> str:
    """OAuth 인증 코드를 사용하여 Refresh Token을 발급받습니다.

    Args:
        auth_code: Google OAuth에서 받은 인증 코드
        client_id: OAuth2 클라이언트 ID
        client_secret: OAuth2 클라이언트 시크릿
        redirect_uri: 리다이렉트 URI (기본값: urn:ietf:wg:oauth:2.0:oob)
    """
    try:
        import requests

        # redirect_uri가 제공되지 않으면 환경변수 사용
        if redirect_uri is None:
            redirect_uri = DEFAULT_REDIRECT_URI

        token_url = "https://oauth2.googleapis.com/token"

        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        response = requests.post(token_url, data=data)

        if response.status_code == 200:
            token_data = response.json()
            refresh_token = token_data.get('refresh_token')
            access_token = token_data.get('access_token')

            if refresh_token:
                return f"""토큰 발급 성공!

Refresh Token: {refresh_token}
Access Token: {access_token}
Token Type: {token_data.get('token_type', 'Bearer')}
Expires In: {token_data.get('expires_in', 'N/A')} seconds

이 refresh_token을 gmail_authenticate_with_refresh_token에 사용하세요."""
            else:
                return f"Refresh Token이 응답에 없습니다. 응답: {token_data}"
        else:
            return f"토큰 발급 실패: {response.status_code} - {response.text}"

    except Exception as e:
        return f"토큰 발급 실패: {str(e)}"

@mcp.tool()
def get_oauth_url_for_refresh_token(client_id: str, redirect_uri: str = None) -> str:
    """Refresh Token 발급을 위한 OAuth URL을 생성합니다.

    Args:
        client_id: OAuth2 클라이언트 ID
        redirect_uri: 리다이렉트 URI (기본값: urn:ietf:wg:oauth:2.0:oob)
    """
    try:
        import urllib.parse

        # redirect_uri가 제공되지 않으면 환경변수 사용
        if redirect_uri is None:
            redirect_uri = DEFAULT_REDIRECT_URI

        scopes = ' '.join(SCOPES)

        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scopes,
            'response_type': 'code',
            'access_type': 'offline'  # refresh token을 받기 위해 필수
        }

        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"

        return f"""OAuth 인증 URL이 생성되었습니다.

1. 다음 URL을 브라우저에서 열어주세요:
{auth_url}

2. Google 로그인 및 권한 승인을 완료하세요.

3. 브라우저에 표시되는 인증 코드를 복사하세요.

4. get_refresh_token_from_auth_code 도구에 인증 코드를 입력하여 refresh token을 받으세요.

참고: access_type=offline과 prompt=consent 옵션으로 refresh token 발급이 보장됩니다."""

    except Exception as e:
        return f"OAuth URL 생성 실패: {str(e)}"

@mcp.tool()
def read_emails(query: str = "", max_results: int = 10) -> str:
    """Gmail에서 이메일을 조회합니다.

    Args:
        query: Gmail 검색 쿼리 (예: "from:example@gmail.com", "is:unread", "subject:urgent")
        max_results: 조회할 최대 이메일 수 (기본값: 10)
    """
    try:
        if not gmail_service.service:
            return "Gmail 인증이 필요합니다. 먼저 gmail_authenticate를 실행하세요."

        messages = gmail_service.get_messages(query, max_results)

        if not messages:
            return "조회된 이메일이 없습니다."

        result = f"총 {len(messages)}개의 이메일을 조회했습니다:\n\n"

        for i, msg in enumerate(messages, 1):
            result += f"[{i}] ID: {msg['id']}\n"
            result += f"    제목: {msg['subject']}\n"
            result += f"    발신자: {msg['sender']}\n"
            result += f"    날짜: {msg['date']}\n"
            result += f"    미리보기: {msg['snippet']}\n"
            if msg['body']:
                result += f"    본문: {msg['body']}\n"
            result += "\n" + "-"*50 + "\n\n"

        return result

    except Exception as e:
        return f"이메일 조회 실패: {str(e)}"

@mcp.tool()
def send_email(to: str, subject: str, body: str, html_body: Optional[str] = None) -> str:
    """Gmail을 통해 이메일을 발송합니다.

    Args:
        to: 수신자 이메일 주소
        subject: 이메일 제목
        body: 이메일 본문 (텍스트)
        html_body: HTML 형식의 이메일 본문 (선택사항)
    """
    try:
        if not gmail_service.service:
            return "Gmail 인증이 필요합니다. 먼저 gmail_authenticate를 실행하세요."

        result = gmail_service.send_message(to, subject, body, html_body)
        return f"이메일이 성공적으로 발송되었습니다. 메시지 ID: {result['id']}"

    except Exception as e:
        return f"이메일 발송 실패: {str(e)}"

@mcp.tool()
def get_email_by_id(email_id: str) -> str:
    """특정 이메일 ID로 이메일의 전체 내용을 조회합니다.

    Args:
        email_id: 조회할 이메일의 ID
    """
    try:
        if not gmail_service.service:
            return "Gmail 인증이 필요합니다. 먼저 gmail_authenticate를 실행하세요."

        message = gmail_service.service.users().messages().get(
            userId='me', id=email_id, format='full'
        ).execute()

        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        to = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')

        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        else:
            if message['payload']['mimeType'] == 'text/plain':
                if 'data' in message['payload']['body']:
                    body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        result = f"이메일 상세 정보:\n\n"
        result += f"ID: {email_id}\n"
        result += f"제목: {subject}\n"
        result += f"발신자: {sender}\n"
        result += f"수신자: {to}\n"
        result += f"날짜: {date}\n"
        result += f"본문:\n{body}\n"

        return result

    except Exception as e:
        return f"이메일 조회 실패: {str(e)}"

@mcp.tool()
def search_emails(sender: Optional[str] = None, subject_contains: Optional[str] = None,
                  is_unread: bool = False, has_attachment: bool = False,
                  after_date: Optional[str] = None, before_date: Optional[str] = None,
                  max_results: int = 10) -> str:
    """다양한 조건으로 이메일을 검색합니다.

    Args:
        sender: 발신자 이메일 주소
        subject_contains: 제목에 포함될 키워드
        is_unread: 읽지 않은 이메일만 검색 여부
        has_attachment: 첨부파일이 있는 이메일만 검색 여부
        after_date: 이 날짜 이후의 이메일 (YYYY/MM/DD 형식)
        before_date: 이 날짜 이전의 이메일 (YYYY/MM/DD 형식)
        max_results: 조회할 최대 이메일 수
    """
    try:
        if not gmail_service.service:
            return "Gmail 인증이 필요합니다. 먼저 gmail_authenticate를 실행하세요."

        query_parts = []

        if sender:
            query_parts.append(f"from:{sender}")
        if subject_contains:
            query_parts.append(f"subject:{subject_contains}")
        if is_unread:
            query_parts.append("is:unread")
        if has_attachment:
            query_parts.append("has:attachment")
        if after_date:
            query_parts.append(f"after:{after_date}")
        if before_date:
            query_parts.append(f"before:{before_date}")

        query = " ".join(query_parts)

        return read_emails(query, max_results)

    except Exception as e:
        return f"이메일 검색 실패: {str(e)}"

@mcp.resource("gmail://info")
def get_gmail_info() -> str:
    """Gmail MCP 서버 정보를 제공하는 리소스"""
    return """
    Gmail MCP Server 정보
    ====================

    이 서버는 Gmail API를 통해 이메일 읽기 및 발송 기능을 제공합니다.

    제공하는 도구:
    - gmail_authenticate: Gmail API 인증
    - read_emails: 이메일 조회 (검색 쿼리 지원)
    - send_email: 이메일 발송 (텍스트/HTML 지원)
    - get_email_by_id: 특정 ID로 이메일 상세 조회
    - search_emails: 다양한 조건으로 이메일 검색

    사용 전 준비사항:
    1. Google Cloud Console에서 Gmail API 활성화
    2. OAuth2 클라이언트 자격 증명 다운로드 (credentials.json)
    3. gmail_authenticate 도구로 인증 수행

    지원하는 검색 조건:
    - 발신자별 검색
    - 제목 키워드 검색
    - 읽지 않은 메일 검색
    - 첨부파일 포함 메일 검색
    - 날짜 범위 검색
    """

if __name__ == "__main__":
    mcp.run(transport="streamable-http")