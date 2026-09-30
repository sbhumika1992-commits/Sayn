import cv2
import time
import math
import mediapipe as mp
import requests
import io
import sounddevice as sd
import soundfile as sf
import tempfile
import threading
import os


# ==========================================
# SAYN - STEP 4
# Hand Sign → Letter Prototype
# ==========================================

MODEL_PATH = "hand_landmarker.task"

CLAP_DISTANCE = 0.20
RELEASE_DISTANCE = 0.28
CLAP_COOLDOWN = 0.70
TRANSCRIBE_API_URL = "http://127.0.0.1:8000/transcribe"
CHAT_API_URL = "http://127.0.0.1:8000/chat"
SPEAK_API_URL = "http://127.0.0.1:8000/speak"

# Time required before accepting a new letter
LETTER_COOLDOWN = 1.0

AI_RECORD_SECONDS = 5
AI_SAMPLE_RATE = 16000
AI_COOLDOWN = 3.0


# ==========================================
# MediaPipe
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


# ==========================================
# Utility
# ==========================================

def distance(p1, p2):

    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def get_fingers(hand):

    wrist = hand[0]

    thumb_tip = hand[4]
    thumb_ip = hand[3]

    thumb_extended = (
        distance(thumb_tip, wrist)
        > distance(thumb_ip, wrist) * 1.15
    )

    index_extended = hand[8].y < hand[6].y
    middle_extended = hand[12].y < hand[10].y
    ring_extended = hand[16].y < hand[14].y
    pinky_extended = hand[20].y < hand[18].y

    return [
        int(thumb_extended),
        int(index_extended),
        int(middle_extended),
        int(ring_extended),
        int(pinky_extended)
    ]


# ==========================================
# Basic Gesture Recognition
# ==========================================

def recognize_gesture(fingers):

    thumb, index, middle, ring, pinky = fingers

    total = sum(fingers)

    # ✋ STOP
    if total == 5:
        return "STOP"

    # ✊ START
    if total == 0:
        return "START"

    # 👍 OKAY
    if (
        thumb == 1
        and index == 0
        and middle == 0
        and ring == 0
        and pinky == 0
    ):
        return "OKAY"

    # ☝️ AI VOICE
    if (
        thumb == 0
        and index == 1
        and middle == 0
        and ring == 0
        and pinky == 0
    ):
        return "AI VOICE"

    return "UNKNOWN"


# ==========================================
# Prototype Letter Recognition
# ==========================================

def recognize_letter(hand, fingers):

    thumb, index, middle, ring, pinky = fingers

    # --------------------------------------
    # H
    # Index + Middle
    # --------------------------------------

    if (
        index == 1
        and middle == 1
        and ring == 0
        and pinky == 0
        and thumb == 0
    ):
        return "H"


    # --------------------------------------
    # E
    # Four fingers up, thumb folded
    # --------------------------------------

    if (
        thumb == 0
        and index == 1
        and middle == 1
        and ring == 1
        and pinky == 1
    ):
        return "E"


    # --------------------------------------
    # L
    # Thumb + Index
    # --------------------------------------

    if (
        thumb == 1
        and index == 1
        and middle == 0
        and ring == 0
        and pinky == 0
    ):
        return "L"


    # --------------------------------------
    # P
    # Index + Middle + Ring
    # --------------------------------------

    if (
        thumb == 0
        and index == 1
        and middle == 1
        and ring == 1
        and pinky == 0
    ):
        return "P"


    # --------------------------------------
    # O
    # Thumb + Index pinch
    # --------------------------------------

    thumb_tip = hand[4]
    index_tip = hand[8]

    pinch_distance = distance(
        thumb_tip,
        index_tip
    )

    if pinch_distance < 0.07:

        return "O"


    return None



# ==========================================
# AI VOICE FUNCTIONS
# ==========================================

def record_voice():

    print()
    print("🎙️ SAYN IS LISTENING...")
    print(f"Speak now for {AI_RECORD_SECONDS} seconds.")

    try:

        recording = sd.rec(
            int(AI_RECORD_SECONDS * AI_SAMPLE_RATE),
            samplerate=AI_SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        print("✅ Recording finished.")

        return recording

    except Exception as error:

        print("❌ MICROPHONE ERROR:")
        print(repr(error))

        return None


def save_wav(recording):

    try:

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        filename = temp_file.name
        temp_file.close()

        sf.write(
            filename,
            recording,
            AI_SAMPLE_RATE
        )

        return filename

    except Exception as error:

        print("❌ WAV ERROR:")
        print(repr(error))

        return None


def transcribe_voice(filename):

    try:

        print("🧠 Sending voice to Whisper...")

        with open(filename, "rb") as audio_file:

            response = requests.post(
                TRANSCRIBE_API_URL,
                files={
                    "file": (
                        "sayn_voice.wav",
                        audio_file,
                        "audio/wav"
                    )
                },
                timeout=40
            )

        response.raise_for_status()

        data = response.json()

        text = (data.get("text") or "").strip()

        print("📝 YOU SAID:", text)

        return text

    except Exception as error:

        print("❌ TRANSCRIPTION ERROR:")
        print(repr(error))

        return ""


def ask_ai(question):

    try:

        print("🤖 ASKING SAYN AI...")
        print("Question:", question)

        response = requests.post(
            CHAT_API_URL,
            json={"message": question},
            timeout=40
        )

        response.raise_for_status()

        data = response.json()

        answer = (data.get("response") or "").strip()

        print("🤖 SAYN ANSWER:", answer)

        return answer

    except Exception as error:

        print("❌ AI ERROR:")
        print(repr(error))

        return ""


def speak_text(text):

    try:

        print("🔊 SAYN SPEAKING:")
        print(text)

        response = requests.post(
            SPEAK_API_URL,
            json={"message": text},
            timeout=40
        )

        response.raise_for_status()

        audio_data = io.BytesIO(response.content)

        audio, sample_rate = sf.read(
            audio_data,
            dtype="float32"
        )

        sd.play(audio, sample_rate)
        sd.wait()

        print("✅ Speech finished.")

    except Exception as error:

        print("❌ SPEECH ERROR:")
        print(repr(error))


def ai_voice_conversation():

    filename = None

    try:

        recording = record_voice()

        if recording is None:
            return

        filename = save_wav(recording)

        if filename is None:
            return

        question = transcribe_voice(filename)

        if not question:
            print("⚠️ No speech detected.")
            return

        answer = ask_ai(question)

        if not answer:
            return

        speak_text(answer)

    except Exception as error:

        print("❌ AI VOICE ERROR:")
        print(repr(error))

    finally:

        if filename:

            try:
                os.remove(filename)
            except:
                pass


# ==========================================
# Draw Hand
# ==========================================

def draw_hand(frame, hand):

    connections = [

        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        (0, 17)
    ]


    for landmark in hand:

        x = int(
            landmark.x * frame.shape[1]
        )

        y = int(
            landmark.y * frame.shape[0]
        )

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )


    for start, end in connections:

        x1 = int(
            hand[start].x * frame.shape[1]
        )

        y1 = int(
            hand[start].y * frame.shape[0]
        )

        x2 = int(
            hand[end].x * frame.shape[1]
        )

        y2 = int(
            hand[end].y * frame.shape[0]
        )

        cv2.line(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )


# ==========================================
# Camera
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("❌ Camera could not be opened.")
    raise SystemExit


print()
print("==========================================")
print("             SAYN - STEP 4")
print("        HAND SIGN PROTOTYPE")
print("==========================================")
print()
print("👏 Clap       = Activate / Deactivate")
print("✊ START      = Start letter recognition")
print("✋ STOP       = Sentence full stop")
print("👍 OKAY       = Space / Confirm")
print("☝️ AI VOICE   = AI Voice")
print()
print("Prototype letters:")
print("H  = Index + Middle")
print("E  = Four fingers, thumb folded")
print("L  = Thumb + Index")
print("P  = Index + Middle + Ring")
print("O  = Thumb + Index pinch")
print()
print("Press Q to quit.")
print()


# ==========================================
# State
# ==========================================

sayn_active = False

letter_mode = False

sentence = ""

last_clap_time = 0
last_letter_time = 0
last_ai_time = 0
ai_busy = False
clap_in_progress = False

start_time = time.time()


# ==========================================
# Main Loop
# ==========================================

with HandLandmarker.create_from_options(options) as detector:

    while True:

        success, frame = cap.read()

        if not success:

            print("❌ Camera frame error.")
            break


        frame = cv2.flip(frame, 1)


        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        timestamp_ms = int(
            (time.time() - start_time) * 1000
        )


        result = detector.detect_for_video(
            mp_image,
            timestamp_ms
        )


        gesture = "NO HAND"
        detected_letter = None


        # ==================================
        # CLAP
        # ==================================

        if len(result.hand_landmarks) >= 2:

            hand1 = result.hand_landmarks[0]
            hand2 = result.hand_landmarks[1]

            # Use palm-center distance for more reliable two-hand clap detection.
            palm_distance = distance(
                hand1[9],
                hand2[9]
            )

            current_time = time.time()

            # Hands come close together = clap event.
            if palm_distance < CLAP_DISTANCE:

                if (
                    not clap_in_progress
                    and
                    current_time - last_clap_time > CLAP_COOLDOWN
                ):

                    clap_in_progress = True
                    sayn_active = not sayn_active
                    last_clap_time = current_time

                    if not sayn_active:

                        letter_mode = False

                        print("👏 CLAP")
                        print("🔴 SAYN INACTIVE")

                    else:

                        print("👏 CLAP")
                        print("🟢 SAYN ACTIVE")

            # Require separation before another clap can be detected.
            elif palm_distance > RELEASE_DISTANCE:

                clap_in_progress = False


        # ==================================
        # HAND PROCESSING
        # ==================================

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            draw_hand(
                frame,
                hand
            )


            fingers = get_fingers(hand)

            gesture = recognize_gesture(
                fingers
            )


            # ==================================
            # AI VOICE
            # ==================================

            current_time = time.time()

            if (
                sayn_active
                and gesture == "AI VOICE"
                and not ai_busy
                and current_time - last_ai_time > AI_COOLDOWN
            ):

                ai_busy = True
                last_ai_time = current_time

                print()
                print("☝️ AI VOICE ACTIVATED")

                def run_ai():

                    global ai_busy

                    try:
                        ai_voice_conversation()

                    finally:
                        ai_busy = False

                threading.Thread(
                    target=run_ai,
                    daemon=True
                ).start()


            # ==================================
            # START LETTER MODE
            # ==================================

            if sayn_active and not letter_mode:

                if gesture == "START":

                    letter_mode = True

                    sentence = ""

                    print()
                    print("✊ START")
                    print("🟢 LETTER RECOGNITION STARTED")


            # ==================================
            # LETTER MODE
            # ==================================

            elif sayn_active and letter_mode:

                current_time = time.time()


                # ------------------------------
                # STOP = FULL STOP
                # ------------------------------

                if gesture == "STOP":

                    if sentence and not sentence.endswith("."):

                        sentence += "."

                        print(
                            "✋ STOP →",
                            sentence
                        )


                    letter_mode = False


                # ------------------------------
                # OKAY = SPACE
                # ------------------------------

                elif gesture == "OKAY":

                    if (
                        sentence
                        and
                        not sentence.endswith(" ")
                        and
                        not sentence.endswith(".")
                    ):

                        sentence += " "

                        print(
                            "👍 SPACE →",
                            repr(sentence)
                        )


                # ------------------------------
                # LETTER
                # ------------------------------

                else:

                    detected_letter = recognize_letter(
                        hand,
                        fingers
                    )


                    if (
                        detected_letter
                        and
                        current_time - last_letter_time
                        > LETTER_COOLDOWN
                    ):

                        sentence += detected_letter

                        last_letter_time = current_time

                        print(
                            "LETTER:",
                            detected_letter,
                            "→",
                            sentence
                        )


        # ==================================
        # STATUS
        # ==================================

        if sayn_active:

            if ai_busy:
                status_text = "SAYN - AI VOICE"
            else:
                status_text = "SAYN ACTIVE"
            status_color = (0, 255, 0)

        else:

            status_text = "SAYN INACTIVE"
            status_color = (0, 0, 255)


        cv2.putText(
            frame,
            status_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            status_color,
            2
        )


        # ==================================
        # Mode
        # ==================================

        if letter_mode:

            mode_text = "LETTER MODE"

        else:

            mode_text = "READY"


        cv2.putText(
            frame,
            mode_text,
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )


        # ==================================
        # Current Gesture
        # ==================================

        if sayn_active:

            cv2.putText(
                frame,
                f"Gesture: {gesture}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


        cv2.putText(
            frame,
            f"Hands detected: {len(result.hand_landmarks)}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ==================================
        # Sentence
        # ==================================

        cv2.rectangle(
            frame,
            (15, frame.shape[0] - 100),
            (frame.shape[1] - 15, frame.shape[0] - 15),
            (20, 20, 20),
            -1
        )


        cv2.putText(
            frame,
            sentence if sentence else "_",
            (30, frame.shape[0] - 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 255, 255),
            2
        )


        cv2.putText(
            frame,
            "👏 ON/OFF   ✊ START   👍 SPACE   ✋ END",
            (20, frame.shape[0] - 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )


        cv2.imshow(
            "SAYN",
            frame
        )


        # ==================================
        # Q = QUIT
        # ==================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ==========================================
# Cleanup
# ==========================================

cap.release()

cv2.destroyAllWindows()

print()
print("SAYN stopped.")