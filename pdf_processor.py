"""
PDF Processor - Extract text, figures, and structure from PDF articles
"""

import os
import logging
import base64
from pathlib import Path
from typing import Dict, List, Tuple
import fitz  # PyMuPDF
from PIL import Image
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF files to extract text and figures"""

    # Minimum image size to consider (pixels)
    MIN_IMAGE_WIDTH = 200
    MIN_IMAGE_HEIGHT = 200

    # Maximum figures to extract per PDF
    MAX_FIGURES = 10

    def __init__(self, pdf_path: str):
        """
        Initialize PDF processor

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.doc = fitz.open(str(self.pdf_path))
        logger.info(f"Opened PDF: {self.pdf_path.name} ({len(self.doc)} pages)")

    def extract_text(self) -> str:
        """
        Extract all text from PDF

        Returns:
            Full text content
        """
        try:
            logger.info(f"Extracting text from {self.pdf_path.name}")

            text_parts = []

            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                text = page.get_text()
                text_parts.append(text)

            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters of text")

            return full_text

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    def extract_figures(self) -> List[Dict]:
        """
        Extract figures/images from PDF

        Returns:
            List of figure dictionaries with image data and metadata
        """
        try:
            logger.info(f"Extracting figures from {self.pdf_path.name}")

            figures = []
            image_count = 0

            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    # Stop if we've extracted enough figures
                    if len(figures) >= self.MAX_FIGURES:
                        break

                    try:
                        xref = img[0]
                        base_image = self.doc.extract_image(xref)

                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        # Load image to check size
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        width, height = pil_image.size

                        # Filter out small images (logos, icons, etc.)
                        if width < self.MIN_IMAGE_WIDTH or height < self.MIN_IMAGE_HEIGHT:
                            logger.debug(f"Skipping small image: {width}x{height}")
                            continue

                        # Convert to JPEG if needed
                        if image_ext not in ["jpeg", "jpg", "png"]:
                            logger.debug(f"Converting {image_ext} to JPEG")
                            buffer = io.BytesIO()
                            pil_image.convert('RGB').save(buffer, format='JPEG', quality=85)
                            image_bytes = buffer.getvalue()
                            image_ext = "jpeg"

                        # Resize if too large (max 2000px on longest side)
                        max_size = 2000
                        if max(width, height) > max_size:
                            ratio = max_size / max(width, height)
                            new_size = (int(width * ratio), int(height * ratio))
                            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

                            buffer = io.BytesIO()
                            pil_image.save(buffer, format='JPEG', quality=85)
                            image_bytes = buffer.getvalue()
                            width, height = new_size

                        # Try to extract caption (text below image)
                        caption = self._extract_caption(page, img, page_num)

                        # Encode to base64
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                        figures.append({
                            "figure_num": len(figures) + 1,
                            "page": page_num + 1,
                            "index": img_index,
                            "width": width,
                            "height": height,
                            "format": image_ext,
                            "size_bytes": len(image_bytes),
                            "caption": caption,
                            "data": image_base64
                        })

                        image_count += 1
                        logger.debug(f"Extracted figure {len(figures)}: {width}x{height}px from page {page_num + 1}")

                    except Exception as e:
                        logger.warning(f"Error extracting image on page {page_num + 1}: {e}")
                        continue

                # Break if we have enough figures
                if len(figures) >= self.MAX_FIGURES:
                    break

            logger.info(f"Extracted {len(figures)} figures")
            return figures

        except Exception as e:
            logger.error(f"Error extracting figures: {e}")
            return []

    def _extract_caption(self, page, img, page_num: int) -> str:
        """
        Extract caption text near an image

        Args:
            page: PyMuPDF page object
            img: Image info
            page_num: Page number

        Returns:
            Caption text if found, empty string otherwise
        """
        try:
            # Get image position on page
            img_rect = page.get_image_rects(img[0])

            if not img_rect:
                return ""

            # Get text below image
            page_rect = page.rect
            search_rect = fitz.Rect(
                0,
                img_rect[0].y1,  # Start below image
                page_rect.width,
                min(img_rect[0].y1 + 100, page_rect.height)  # Search 100px below
            )

            text = page.get_textbox(search_rect)

            if text:
                # Clean up caption
                text = text.strip()
                # Look for common caption patterns
                if any(text.lower().startswith(prefix) for prefix in ['figure', 'fig.', 'fig ']):
                    # Take first sentence or first 200 chars
                    if '.' in text:
                        caption = text.split('.')[0] + '.'
                    else:
                        caption = text[:200]
                    return caption

            return ""

        except Exception as e:
            logger.debug(f"Could not extract caption: {e}")
            return ""

    def extract_sections(self) -> Dict[str, str]:
        """
        Extract structured sections from PDF (Abstract, Methods, Results, etc.)

        Returns:
            Dictionary mapping section names to content
        """
        try:
            logger.info("Extracting sections")

            full_text = self.extract_text()

            sections = {}
            section_headers = [
                "ABSTRACT",
                "INTRODUCTION",
                "METHODS",
                "MATERIALS AND METHODS",
                "RESULTS",
                "DISCUSSION",
                "CONCLUSION",
                "CONCLUSIONS"
            ]

            lines = full_text.split('\n')
            current_section = "PREAMBLE"
            current_text = []

            for line in lines:
                line_upper = line.strip().upper()

                # Check if this line is a section header
                if any(line_upper.startswith(header) for header in section_headers):
                    # Save previous section
                    if current_text:
                        sections[current_section] = '\n'.join(current_text).strip()

                    # Start new section
                    current_section = line_upper.split()[0]
                    current_text = []
                else:
                    current_text.append(line)

            # Save last section
            if current_text:
                sections[current_section] = '\n'.join(current_text).strip()

            logger.info(f"Extracted {len(sections)} sections")
            return sections

        except Exception as e:
            logger.error(f"Error extracting sections: {e}")
            return {}

    def get_metadata(self) -> Dict:
        """
        Extract PDF metadata

        Returns:
            Dictionary with metadata
        """
        try:
            metadata = {
                "title": self.doc.metadata.get("title", ""),
                "author": self.doc.metadata.get("author", ""),
                "subject": self.doc.metadata.get("subject", ""),
                "pages": len(self.doc),
                "file_size": self.pdf_path.stat().st_size,
            }
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}

    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()
            logger.debug(f"Closed PDF: {self.pdf_path.name}")


def extract_pdf_content(pdf_path: str) -> Dict:
    """
    Convenience function to extract all content from a PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with text, figures, sections, and metadata
    """
    processor = PDFProcessor(pdf_path)

    try:
        content = {
            "text": processor.extract_text(),
            "figures": processor.extract_figures(),
            "sections": processor.extract_sections(),
            "metadata": processor.get_metadata(),
        }
        return content
    finally:
        processor.close()


if __name__ == "__main__":
    # Test the processor
    import sys

    print("Testing PDF Processor...\n")

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Look for any PDF in pdfs directory
        pdf_dir = Path("pdfs")
        if pdf_dir.exists():
            pdfs = list(pdf_dir.glob("*.pdf"))
            if pdfs:
                pdf_path = str(pdfs[0])
            else:
                print("No PDFs found in pdfs/ directory")
                sys.exit(1)
        else:
            print("Usage: python pdf_processor.py <path_to_pdf>")
            sys.exit(1)

    print(f"Processing: {pdf_path}\n")

    try:
        content = extract_pdf_content(pdf_path)

        print(f"✓ Extracted {len(content['text'])} characters of text")
        print(f"✓ Found {len(content['figures'])} figures")
        print(f"✓ Identified {len(content['sections'])} sections:")
        for section in content['sections'].keys():
            print(f"    - {section}")
        print(f"✓ Metadata:")
        for key, value in content['metadata'].items():
            print(f"    - {key}: {value}")

        # Show first figure info
        if content['figures']:
            fig = content['figures'][0]
            print(f"\nFirst figure:")
            print(f"  - Page: {fig['page']}")
            print(f"  - Size: {fig['width']}x{fig['height']}px")
            print(f"  - Caption: {fig['caption'][:100]}...")

    except Exception as e:
        print(f"✗ Error: {e}")
