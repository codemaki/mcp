from mcp.server.fastmcp import FastMCP
from PIL import Image
import cv2
import numpy as np
import base64
import io
from typing import Optional, List, Dict, Any
import os
import tempfile

# FastMCP 인스턴스를 생성
mcp = FastMCP("Image Converter MCP Server", host="0.0.0.0", port=8000)


@mcp.tool()
def convert_image_format(
    image_data: str,
    output_format: str = "PNG",
    quality: int = 95
) -> str:
    """
    이미지 포맷을 변환합니다.
    
    Args:
        image_data: Base64로 인코딩된 이미지 데이터
        output_format: 출력 포맷 (PNG, JPEG, JPG, WEBP, BMP, TIFF)
        quality: JPEG 품질 (1-100, 기본값: 95)
    
    Returns:
        Base64로 인코딩된 변환된 이미지 데이터
    """
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # RGB 모드로 변환 (JPEG의 경우)
        if output_format.upper() in ("JPEG", "JPG") and image.mode in ("RGBA", "LA", "P"):
            # 투명도가 있는 이미지를 JPEG로 변환할 때는 흰색 배경 추가
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background
        
        # 이미지 변환
        output_buffer = io.BytesIO()
        
        if output_format.upper() in ("JPEG", "JPG"):
            image.save(output_buffer, format="JPEG", quality=quality, optimize=True)
        else:
            image.save(output_buffer, format=output_format.upper())
        
        # Base64 인코딩
        output_buffer.seek(0)
        converted_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return converted_data
        
    except Exception as e:
        return f"이미지 포맷 변환 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def resize_image(
    image_data: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale_factor: Optional[float] = None,
    maintain_aspect_ratio: bool = True
) -> str:
    """
    이미지 크기를 조정합니다.
    
    Args:
        image_data: Base64로 인코딩된 이미지 데이터
        width: 새로운 너비 (픽셀)
        height: 새로운 높이 (픽셀)
        scale_factor: 크기 배율 (예: 0.5는 50% 크기)
        maintain_aspect_ratio: 종횡비 유지 여부
    
    Returns:
        Base64로 인코딩된 크기 조정된 이미지 데이터
    """
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        original_width, original_height = image.size
        
        # 크기 계산
        if scale_factor is not None:
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
        else:
            if width is None and height is None:
                return "너비, 높이, 또는 배율 중 하나를 지정해야 합니다."
            
            if maintain_aspect_ratio:
                if width is not None and height is not None:
                    # 둘 다 지정된 경우, 종횡비를 유지하면서 더 작은 크기에 맞춤
                    scale_w = width / original_width
                    scale_h = height / original_height
                    scale = min(scale_w, scale_h)
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                elif width is not None:
                    scale = width / original_width
                    new_width = width
                    new_height = int(original_height * scale)
                else:  # height is not None
                    scale = height / original_height
                    new_width = int(original_width * scale)
                    new_height = height
            else:
                new_width = width or original_width
                new_height = height or original_height
        
        # 이미지 리사이즈
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Base64 인코딩
        output_buffer = io.BytesIO()
        resized_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        resized_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return resized_data
        
    except Exception as e:
        return f"이미지 크기 조정 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def crop_image(
    image_data: str,
    x: int,
    y: int,
    width: int,
    height: int
) -> str:
    """
    이미지를 자릅니다.
    
    Args:
        image_data: Base64로 인코딩된 이미지 데이터
        x: 자를 영역의 왼쪽 상단 x 좌표
        y: 자를 영역의 왼쪽 상단 y 좌표
        width: 자를 영역의 너비
        height: 자를 영역의 높이
    
    Returns:
        Base64로 인코딩된 자른 이미지 데이터
    """
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # 이미지 크기 확인
        img_width, img_height = image.size
        if x + width > img_width or y + height > img_height:
            return f"잘라낼 영역이 이미지 크기를 초과합니다. 이미지 크기: {img_width}x{img_height}"
        
        # 이미지 자르기
        cropped_image = image.crop((x, y, x + width, y + height))
        
        # Base64 인코딩
        output_buffer = io.BytesIO()
        cropped_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        cropped_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return cropped_data
        
    except Exception as e:
        return f"이미지 자르기 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def rotate_image(
    image_data: str,
    angle: float,
    expand: bool = True
) -> str:
    """
    이미지를 회전합니다.
    
    Args:
        image_data: Base64로 인코딩된 이미지 데이터
        angle: 회전 각도 (도 단위, 양수는 시계방향)
        expand: 회전 후 이미지 크기 확장 여부
    
    Returns:
        Base64로 인코딩된 회전된 이미지 데이터
    """
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # 이미지 회전
        rotated_image = image.rotate(-angle, expand=expand, fillcolor=(255, 255, 255))
        
        # Base64 인코딩
        output_buffer = io.BytesIO()
        rotated_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        rotated_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return rotated_data
        
    except Exception as e:
        return f"이미지 회전 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def get_image_info(image_data: str) -> str:
    """
    이미지 정보를 반환합니다.
    
    Args:
        image_data: Base64로 인코딩된 이미지 데이터
    
    Returns:
        이미지 정보 (크기, 포맷, 모드 등)
    """
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        info = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "size_bytes": len(image_bytes),
            "has_transparency": image.mode in ("RGBA", "LA", "P")
        }
        
        return f"""이미지 정보:
- 크기: {info['width']} x {info['height']} 픽셀
- 포맷: {info['format']}
- 색상 모드: {info['mode']}
- 파일 크기: {info['size_bytes']:,} 바이트
- 투명도: {'있음' if info['has_transparency'] else '없음'}"""
        
    except Exception as e:
        return f"이미지 정보 조회 중 오류가 발생했습니다: {str(e)}"


@mcp.tool()
def apply_filters(
    image_data: str,
    filter_type: str = "blur",
    intensity: float = 1.0
) -> str:
    """
    이미지에 필터를 적용합니다.
    
    Args:
        image_data: Base64로 인코딩된 이미지 데이터
        filter_type: 필터 타입 (blur, sharpen, edge_detect, emboss)
        intensity: 필터 강도 (0.1-5.0)
    
    Returns:
        Base64로 인코딩된 필터가 적용된 이미지 데이터
    """
    try:
        # Base64 디코딩
        image_bytes = base64.b64decode(image_data)
        
        # PIL Image를 OpenCV 형식으로 변환
        pil_image = Image.open(io.BytesIO(image_bytes))
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # 필터 적용
        if filter_type == "blur":
            kernel_size = max(3, int(5 * intensity))
            if kernel_size % 2 == 0:
                kernel_size += 1
            filtered = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
        elif filter_type == "sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * intensity
            filtered = cv2.filter2D(cv_image, -1, kernel)
        elif filter_type == "edge_detect":
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            filtered = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        elif filter_type == "emboss":
            kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]) * intensity
            filtered = cv2.filter2D(cv_image, -1, kernel)
        else:
            return f"지원하지 않는 필터 타입입니다: {filter_type}"
        
        # OpenCV 이미지를 PIL 형식으로 변환
        filtered_rgb = cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
        filtered_pil = Image.fromarray(filtered_rgb)
        
        # Base64 인코딩
        output_buffer = io.BytesIO()
        filtered_pil.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        filtered_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return filtered_data
        
    except Exception as e:
        return f"필터 적용 중 오류가 발생했습니다: {str(e)}"


@mcp.resource("image-converter://info")
def get_server_info() -> str:
    """서버 정보를 제공하는 리소스"""
    return """
    Image Converter MCP Server 정보
    ===============================
    
    이 서버는 이미지 변환 및 처리를 위한 MCP(Model Context Protocol) 서버입니다.
    
    제공하는 도구:
    - convert_image_format: 이미지 포맷 변환 (PNG, JPEG, WEBP, BMP, TIFF)
    - resize_image: 이미지 크기 조정 (너비/높이/배율 지정 가능)
    - crop_image: 이미지 자르기
    - rotate_image: 이미지 회전
    - get_image_info: 이미지 정보 조회
    - apply_filters: 이미지 필터 적용 (블러, 샤프닝, 엣지 검출, 엠보싱)
    
    지원하는 이미지 포맷:
    - 입력: PNG, JPEG, WEBP, BMP, TIFF, GIF 등
    - 출력: PNG, JPEG, WEBP, BMP, TIFF
    
    사용법:
    모든 이미지 데이터는 Base64로 인코딩되어 전달되어야 합니다.
    """


if __name__ == "__main__":
    """서버를 실행합니다."""
    mcp.run(transport="streamable-http")
