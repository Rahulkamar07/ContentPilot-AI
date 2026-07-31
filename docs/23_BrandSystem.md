# ContentPilot AI - Workspace Brand & Style System Specification

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-23-BRAND-SYSTEM` |
| **Author** | Principal Product Designer & Software Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Design Lead | Initial brand engine & watermark overlay specification. |

---

## 1. Watermark & Logo Overlay Engine

Every generated editorial image passes through the **Branding Service** (`app/services/branding_service.py`) before storage upload.

### Watermark Positioning Grid Layout

```
+-------------------------------------------------------+
|  [ TOP_LEFT ]                   [ TOP_RIGHT ]         |
|                                                       |
|                                                       |
|                     [ CENTER ]                        |
|                                                       |
|                                                       |
|  [ BOTTOM_LEFT ]                [ BOTTOM_RIGHT * ]    |
+-------------------------------------------------------+
* Default position: BOTTOM_RIGHT with 20px padding and 85% opacity
```

### PIL Branding Implementation (`app/services/branding_service.py`)

```python
from PIL import Image, ImageEnhance
import io

class BrandingService:
    """Overlays workspace logo watermark onto synthesized AI artwork."""

    def apply_watermark(
        self,
        base_image_bytes: bytes,
        logo_image_bytes: bytes,
        position: str = "BOTTOM_RIGHT",
        opacity: float = 0.85,
    ) -> bytes:
        base_img = Image.open(io.BytesIO(base_image_bytes)).convert("RGBA")
        logo_img = Image.open(io.BytesIO(logo_image_bytes)).convert("RGBA")

        # Resize logo to 15% of base image width maintaining aspect ratio
        target_width = int(base_img.width * 0.15)
        w_percent = target_width / float(logo_img.width)
        target_height = int(float(logo_img.height) * float(w_percent))
        logo_resized = logo_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Apply opacity enhancement
        alpha = logo_resized.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        logo_resized.putalpha(alpha)

        # Calculate position coordinates
        padding = 24
        if position == "BOTTOM_RIGHT":
            x = base_img.width - logo_resized.width - padding
            y = base_img.height - logo_resized.height - padding
        elif position == "TOP_RIGHT":
            x = base_img.width - logo_resized.width - padding
            y = padding
        else:
            x = base_img.width - logo_resized.width - padding
            y = base_img.height - logo_resized.height - padding

        # Composite image
        base_img.paste(logo_resized, (x, y), logo_resized)

        # Export as compressed WEBP
        output_buffer = io.BytesIO()
        base_img.convert("RGB").save(output_buffer, format="WEBP", quality=85)
        return output_buffer.getvalue()
```

---

## 2. Brand Tone & Caption Presets

Workspaces configure brand persona profiles that steer LLM caption generation:

| Preset Name | Target Audience | Sentence Structure | Call-To-Action Style |
| :--- | :--- | :--- | :--- |
| **Professional** | Enterprise Executives, B2B | Concise, factual, formal | *"Read the full analysis in our bio link."* |
| **Casual & Hype** | Gen Z, Social Enthusiasts | Emoji-rich, energetic, hooks | *"Drop your thoughts below! 🔥👇"* |
| **Analytical** | Engineers, Researchers | Bulleted key data points | *"What's your take on this benchmark?"* |
| **Satirical** | Pop Culture, Humor | Witty, sarcastic, punchy | *"Tag a friend who needs to see this!"* |

---

## 3. Image Style Presets

Workspaces select visual aesthetics for generative diffusion prompts:
1. **Photorealistic Editorial**: `"8k photograph, natural studio lighting, highly detailed photography"`
2. **Cyberpunk Neon**: `"Vibrant cyan and magenta neon glow, futuristic aesthetic, dark cinematic lighting"`
3. **Minimalist Vector**: `"Clean vector illustration, flat color palette, modern graphic design"`
4. **Cinematic 3D Render**: `"Octane render, 3D claymation art, soft shadows, vibrant isometric view"`

---

## Document Cross-References
- Global System Blueprint: [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)
- Storage Architecture: [19_Storage.md](file:///d:/Projects/ContentPilot/docs/19_Storage.md)
- UI/UX & Design System: [UI_UX.md](file:///d:/Projects/ContentPilot/docs/UI_UX.md)
