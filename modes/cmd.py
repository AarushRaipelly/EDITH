import sys
import logging

logger = logging.getLogger("EDITH.Modes.CMD")

class CMDInterface:
    def __init__(self, brain) -> None:
        self.brain = brain
        self.voice_mode_active = False

    def start_loop(self) -> None:
        """Launches the CLI loop, parsing inputs directly through the Edith brain."""
        print("=========================================")
        print("  EDITH (CMD Mode) - Online & Secured    ")
        print("  Type 'exit' or 'quit' to close session. ")
        print("=========================================")
        
        from voice.listener import EdithListener
        from voice.speaker import EdithSpeaker
        
        listener = EdithListener()
        speaker = EdithSpeaker()

        while True:
            try:
                # Read console or voice input
                if self.voice_mode_active:
                    print("EDITH CMD (Listening...) > ", end="", flush=True)
                    user_input = listener.listen().strip()
                    if not user_input:
                        print("[No speech detected]")
                        continue
                    print(user_input)
                else:
                    prompt = "EDITH CMD > "
                    user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ("exit", "quit", "abort"):
                    print("Shutting down EDITH session. Goodbye, Boss.")
                    break
                    
                if user_input.lower() in ("activate voice", "switch to voice"):
                    self.voice_mode_active = True
                    speaker.speak("Voice mode activated, Boss. I am listening.")
                    continue
                    
                if user_input.lower() in ("deactivate voice", "switch to text", "deactivate voice mode"):
                    self.voice_mode_active = False
                    print("Voice mode deactivated. Switched to text-only mode.")
                    continue
                    
                # Process input
                response = self.brain.process_input(user_input)
                
                # Output response
                if response:
                    if self.voice_mode_active:
                        speaker.speak(response)
                    else:
                        print(f"\nEDITH: {response}\n")

            except (KeyboardInterrupt, EOFError):
                print("\nSession interrupted. Securing caches.")
                break
            except Exception as e:
                logger.error(f"Error in CMD interface loop: {e}")
                print(f"Error processing command: {e}")
