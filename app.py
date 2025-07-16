
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Navya's 21st Photobooth", layout="centered")
st.title("🎰 Navya's 21st Casino Photobooth 🎲")
st.markdown("Take 3 photos with our casino-themed photobooth!")

# Load overlay text image
overlay_img = Image.open("overlays/navya_text_overlay.png").convert("RGBA")
overlay_np = np.array(overlay_img)

photo_count = st.session_state.get("photo_count", 0)
captured_photos = st.session_state.get("captured_photos", [])

class PhotoTransformer(VideoTransformerBase):
    def __init__(self):
        self.frame = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        if overlay_np.shape[0] < img.shape[0] and overlay_np.shape[1] < img.shape[1]:
            y, x = 20, 20
            h, w = overlay_np.shape[:2]
            overlay_bgr = overlay_np[..., :3]
            mask = overlay_np[..., 3:] / 255.0
            roi = img[y:y+h, x:x+w]
            img[y:y+h, x:x+w] = (roi * (1 - mask) + overlay_bgr * mask).astype(np.uint8)
        self.frame = img
        return img

ctx = webrtc_streamer(key="photo", video_transformer_factory=PhotoTransformer, desired_playing_state=True)

if ctx.video_transformer:
    if "photo_count" not in st.session_state:
        st.session_state["photo_count"] = 0
        st.session_state["captured_photos"] = []

    if st.button("📸 Take Photo") and st.session_state["photo_count"] < 3:
        frame = ctx.video_transformer.frame
        if frame is not None:
            st.session_state["captured_photos"].append(frame)
            st.session_state["photo_count"] += 1
            st.success(f"Photo {st.session_state['photo_count']} taken!")

    if st.session_state["captured_photos"]:
        st.subheader("🖼️ Your Captured Photos:")
        for idx, photo in enumerate(st.session_state["captured_photos"], 1):
            st.image(photo, channels="BGR", caption=f"Photo {idx}")

    if st.session_state["photo_count"] >= 3:
        st.success("You've taken 3 photos! Refresh the page to take more.")
