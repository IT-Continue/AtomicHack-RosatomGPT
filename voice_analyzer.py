from whisper import load_model


def speech_to_text(sound, model):

    return model.transcribe(sound, language="russian", fp16=False)["text"]


def main():
    model = load_model("medium.pt")
    speech_to_text("ru_voice.ogg", model)


if __name__ == "__main__":
    main()
