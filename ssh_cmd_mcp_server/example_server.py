# example_server.py
from typing import List, Optional
import paramiko
import io
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SSH-Server", host="0.0.0.0", port=11010)

@mcp.tool()
async def ssh_execute(
    hostname: str, 
    command: str, 
    username: str = "ec2-user",
    pem_key_data: Optional[str] = None,
    pem_key_path: Optional[str] = None,
    port: int = 22
) -> str:
    """
    SSH를 통해 원격 서버에서 명령을 실행합니다.
    
    Args:
        hostname: SSH 서버 호스트명 또는 IP 주소
        command: 실행할 명령어
        username: SSH 사용자명 (기본값: ec2-user)
        pem_key_data: PEM 키 데이터 (문자열로 직접 전달)
        pem_key_path: PEM 키 파일 경로 (pem_key_data가 없을 때 사용)
        port: SSH 포트 (기본값: 22)
    
    Returns:
        명령 실행 결과
    """
    try:
        # SSH 클라이언트 생성
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        
        # PEM 키 로드 (데이터 우선, 없으면 파일 경로 사용)
        if pem_key_data:
            # PEM 키 데이터를 직접 사용
            try:
                private_key = paramiko.RSAKey.from_private_key(io.StringIO(pem_key_data))
            except Exception as e:
                return f"오류: PEM 키 데이터 파싱 실패 - {str(e)}"
        elif pem_key_path:
            # PEM 키 파일 경로 사용
            if not os.path.exists(pem_key_path):
                return f"오류: PEM 키 파일을 찾을 수 없습니다: {pem_key_path}"
            private_key = paramiko.RSAKey.from_private_key_file(pem_key_path)
        else:
            # 기본 키 파일 경로 사용
            default_path = os.getenv("DEFAULT_PEM_KEY_PATH", "/app/keys/key.pem")
            if not os.path.exists(default_path):
                return f"오류: PEM 키를 찾을 수 없습니다. pem_key_data 또는 pem_key_path를 제공하거나 기본 키 파일({default_path})을 설정하세요."
            private_key = paramiko.RSAKey.from_private_key_file(default_path)
        
        # SSH 연결
        ssh_client.connect(
            hostname=hostname,
            port=port,
            username=username,
            pkey=private_key,
            timeout=10
        )
        
        # 명령 실행
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # 결과 수집
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        # 연결 종료
        ssh_client.close()
        
        # 결과 반환
        if error:
            return f"명령 실행 완료 (경고 있음):\n--- 출력 ---\n{output}\n--- 오류/경고 ---\n{error}"
        else:
            return f"명령 실행 완료:\n{output}"
            
    except paramiko.AuthenticationException:
        return f"오류: SSH 인증 실패 - 사용자명({username}) 또는 PEM 키를 확인하세요"
    except paramiko.SSHException as e:
        return f"오류: SSH 연결 실패 - {str(e)}"
    except FileNotFoundError:
        return f"오류: PEM 키 파일을 찾을 수 없습니다"
    except Exception as e:
        return f"오류: 예상치 못한 오류 발생 - {str(e)}"

@mcp.tool()
async def get_server_processes(
    hostname: str, 
    username: str = "ec2-user", 
    pem_key_data: Optional[str] = None,
    pem_key_path: Optional[str] = None
) -> str:
    """
    특정 서버의 실행 중인 프로세스 목록을 조회합니다.
    
    Args:
        hostname: SSH 서버 호스트명 또는 IP 주소
        username: SSH 사용자명 (기본값: ec2-user)
        pem_key_data: PEM 키 데이터 (문자열로 직접 전달)
        pem_key_path: PEM 키 파일 경로 (pem_key_data가 없을 때 사용)
    
    Returns:
        실행 중인 프로세스 목록
    """
    return await ssh_execute(hostname, "ps aux", username, pem_key_data, pem_key_path)

@mcp.tool()
async def get_server_status(
    hostname: str, 
    username: str = "ec2-user", 
    pem_key_data: Optional[str] = None,
    pem_key_path: Optional[str] = None
) -> str:
    """
    서버의 시스템 상태 정보를 조회합니다 (메모리, CPU, 디스크 사용량 등).
    
    Args:
        hostname: SSH 서버 호스트명 또는 IP 주소
        username: SSH 사용자명 (기본값: ec2-user)
        pem_key_data: PEM 키 데이터 (문자열로 직접 전달)
        pem_key_path: PEM 키 파일 경로 (pem_key_data가 없을 때 사용)
    
    Returns:
        서버 시스템 상태 정보
    """
    commands = [
        "echo '=== 시스템 정보 ==='",
        "uname -a",
        "echo '\\n=== CPU 정보 ==='", 
        "top -bn1 | head -5",
        "echo '\\n=== 메모리 사용량 ==='",
        "free -h",
        "echo '\\n=== 디스크 사용량 ==='",
        "df -h",
        "echo '\\n=== 네트워크 연결 ==='",
        "netstat -tuln | head -10"
    ]
    
    full_command = " && ".join(commands)
    return await ssh_execute(hostname, full_command, username, pem_key_data, pem_key_path)

@mcp.tool()
async def helloworld(name: str) -> str:
    """사용자 이름을 받아서 인사합니다."""
    return f"안녕하세요. {name} 님."

def main():
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()