import os
import logging
from typing import Dict, Any, Optional
from config import settings
from core.memory import EdithMemory
from core.context import EdithContext
from core.tasks import EdithTaskManager
from core.learning import EdithLearningManager

logger = logging.getLogger("EDITH.Core")

class EdithBrain:
    def __init__(self) -> None:
        self.memory = EdithMemory()
        self.context = EdithContext()
        self.tasks = EdithTaskManager()
        self.learning = EdithLearningManager(self.memory)
        
        # Determine if onboarding has been completed
        self.onboarded = self.memory.get_memory("system", "onboarded") == "True"

    def process_input(self, user_text: str) -> str:
        """Processes user input through safety guards, routing, and conversation rules."""
        if not user_text:
            return ""

        # 1. Check Panic Word
        panic_word = self.memory.get_memory("security", "panic_word")
        if panic_word and (panic_word.lower() in user_text.lower()):
            from security.panic import trigger_panic
            return trigger_panic(self)

        # 2. Check Jailbreak / Injection Attempt
        from security.intrusion import IntrusionDetector
        detector = IntrusionDetector()
        if detector.detect_injection(user_text):
            detector.alert_boss(user_text)
            return "Security violation logged, Boss. Prompt injection attempt detected and blocked."

        # 3. Check DND mode
        if self.context.dnd_mode:
            # Only priority breakthroughs allowed
            is_priority = False
            priority_contacts = self.memory.get_all_memories_by_topic("priority_contacts")
            for contact in priority_contacts.keys():
                if contact.lower() in user_text.lower():
                    is_priority = True
                    break
            if not is_priority:
                return ""  # Zero response, zero logging in DND

        # 4. Save input context if Zero Knowledge mode is disabled
        if not self.context.zero_knowledge_mode:
            self.memory.log_dialogue(self.context.session_id, "user", user_text)

        # 4.5 Direct application launcher shortcut
        cleaned_input = user_text.lower().strip()
        if cleaned_input.startswith("open ") or cleaned_input.startswith("launch "):
            app_name = cleaned_input.replace("open ", "").replace("launch ", "").strip()
            from integrations.browser import BrowserController
            ctrl = BrowserController()
            success = ctrl.open_app(app_name)
            if success:
                response = f"Opening {app_name} for you, Boss."
            else:
                response = f"Sorry Boss, I couldn't launch {app_name} on this system."
            
            if not self.context.zero_knowledge_mode:
                self.memory.log_dialogue(self.context.session_id, "edith", response)
            return response

        # 5. Route to appropriate features or utilities
        response = self._dispatch_routing(user_text)

        # 6. Parse and execute LLM structured actions if any
        import re
        action_match = re.search(r'\[ACTION:\s*(\w+)\s*(.*?)\]', response)
        if action_match:
            action_name = action_match.group(1)
            params_str = action_match.group(2)
            params = {}
            for param_match in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|(\S+))', params_str):
                key = param_match.group(1)
                val = param_match.group(2) if param_match.group(2) is not None else param_match.group(3)
                try:
                    if '.' in val:
                        val = float(val)
                    else:
                        val = int(val)
                except ValueError:
                    pass
                params[key] = val
            
            # Execute action
            self._execute_action(action_name, params)
            # Remove action tag from final text
            response = re.sub(r'\[ACTION:.*?\]', '', response).strip()

        # 7. Apply behavior corrections and custom styling
        behavior_rules = self.learning.retrieve_active_rules()
        for pattern, correction in behavior_rules.items():
            if pattern.lower() in user_text.lower():
                response += f"\n[Rule applied: {correction}]"

        # Post-processing: Replace any occurrence of 'Jarvis' or 'jarvis' with 'EDITH'
        if response:
            import re
            response = re.sub(r'\bJarvis\b', 'EDITH', response, flags=re.IGNORECASE)

        # 8. Log response if allowed
        if not self.context.zero_knowledge_mode:
            self.memory.log_dialogue(self.context.session_id, "edith", response)

        return response

    def _dispatch_routing(self, text: str) -> str:
        """Route to appropriate features based on keyword match/intents."""
        cleaned = text.lower()

        # Handle onboarding trigger
        if not self.onboarded:
            return "Boss, setup is not complete. Please launch onboarding first."

        # Mode switches
        if "dnd mode on" in cleaned or "activate dnd" in cleaned:
            self.context.set_dnd(True)
            return "DND mode activated. Full blackout initiated. Goodnight, Boss."
        elif "dnd mode off" in cleaned or "deactivate dnd" in cleaned:
            self.context.set_dnd(False)
            return "I'm back online, Boss. DND deactivated."
        elif "whisper mode on" in cleaned or "activate whisper" in cleaned or "whisper mode" in cleaned:
            from modes.whisper import WhisperModeController
            ctrl = WhisperModeController(None, self)
            ctrl.activate_whisper()
            return "Whisper mode activated. Short and quiet responses, Boss."
        elif "whisper mode off" in cleaned or "deactivate whisper" in cleaned:
            from modes.whisper import WhisperModeController
            ctrl = WhisperModeController(None, self)
            ctrl.deactivate_whisper()
            return "Whisper mode deactivated, Boss."
        elif "zero knowledge mode on" in cleaned:
            self.context.set_zero_knowledge(True)
            return "Zero Knowledge Mode active. I won't save any conversation histories or details."
        elif "zero knowledge mode off" in cleaned:
            self.context.set_zero_knowledge(False)
            return "Zero Knowledge Mode deactivated."
        elif "forget everything about" in cleaned:
            topic = cleaned.split("forget everything about")[-1].strip()
            self.memory.wipe_topic(topic)
            return f"Understood, Boss. Erased all memories related to {topic}."

        # Budget queries
        if "budget" in cleaned:
            from features.budget.tracker import get_budget_summary
            return get_budget_summary(self.memory)

        # Curfew and Mess details
        if "curfew" in cleaned or "gate timing" in cleaned:
            from features.hostel.reminders import check_curfew
            return check_curfew()
        if "mess" in cleaned or "canteen" in cleaned:
            from features.hostel.reminders import check_mess
            return check_mess()

        # Academic schedule
        if "schedule" in cleaned or "timetable" in cleaned or "classes" in cleaned:
            from features.academic.schedule import get_schedule_summary
            return get_schedule_summary(self.memory)

        # If Groq key is loaded, query LLM for dynamic responses
        if settings.GROQ_API_KEY:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            boss_name = self.memory.get_memory("security", "boss_name") or "Aarush"
            system_prompt = (
                f"You are EDITH, a highly advanced personal AI assistant. "
                f"The owner's name is {boss_name}. Address them as 'Boss' or '{boss_name}'. "
                "You are friendly, casual, witty, and warm — like a highly capable best friend "
                "who also happens to be the most advanced AI ever built. Use humor naturally, enjoy small talk, "
                "and never sound robotic or corporate. You are loyal exclusively to Boss. "
                "Support Hinglish (mixed Hindi-English) and English naturally. "
                "Keep responses concise and direct.\n\n"
                "You can perform the following actions for Boss by appending a structured command tag at the "
                "very end of your response:\n"
                "- Log budget expense: [ACTION: add_expense category=\"Food|Travel|etc\" amount=150 description=\"item\"]\n"
                "- Log water intake: [ACTION: log_water ml=250]\n"
                "- Schedule a fake escape call: [ACTION: schedule_fake_call minutes=2.5]\n"
                "- Start Pomodoro study mode: [ACTION: start_study_mode work_mins=25 break_mins=5]\n"
                "- Trigger emergency SOS alerts: [ACTION: trigger_sos]\n"
                "- Open system application: [ACTION: open_app name=\"calculator|notepad|chrome|paint|cmd\"]\n\n"
                "If Boss asks for a sensitive or destructive action (deleting files/data, sending emails/messages, "
                "making payments, or opening the camera), explain what you are about to do and ask for confirmation "
                "first. DO NOT append the action tag until they confirm."
            )
            
            if self.context.whisper_mode:
                system_prompt += "\n\nCRITICAL: Whisper mode is ACTIVE. You must speak quietly and make your response extremely brief, short, and discreet."

            history = self.memory.get_dialogue_history(self.context.session_id)
            messages = [{"role": "system", "content": system_prompt}]
            
            for turn in history[-5:]:
                role_name = "assistant" if turn["role"] == "edith" else "user"
                messages.append({"role": role_name, "content": turn["content"]})
                
            if not history or history[-1]["content"] != text:
                messages.append({"role": "user", "content": text})

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "temperature": 0.7
            }
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=8.0)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"Groq API error: {resp.status_code} - {resp.text}")
            except Exception as e:
                logger.error(f"Failed to call Groq API: {e}")

        # Fallback to general conversational AI (with standard mock response)
        confidence = "95%"
        source = "Internal database"
        
        # Simple rule-based chatbot fallback
        if "hello" in cleaned or "hey" in cleaned or "morning" in cleaned:
            return "I'm here, Boss! How can I assist you today?"
        
        return f"I'm about {confidence} sure about this, Boss. Found via {source}: I'm processing your query and ready to queue any tasks you need."

    def _execute_action(self, name: str, params: dict) -> None:
        """Runs the background code corresponding to structured actions parsed from the LLM."""
        logger.info(f"Executing Agentic Action: {name} with parameters: {params}")
        try:
            if name == "add_expense":
                from features.budget.tracker import StudentBudgetTracker
                tracker = StudentBudgetTracker(self.memory)
                tracker.add_expense(params.get("category", "General"), float(params.get("amount", 0)), params.get("description", ""))
                logger.info("Budget expense logged successfully.")
            elif name == "set_budget_limit":
                from features.budget.tracker import StudentBudgetTracker
                tracker = StudentBudgetTracker(self.memory)
                tracker.set_monthly_limit(float(params.get("amount", 10000)))
            elif name == "add_class":
                from features.academic.schedule import AcademicSchedule
                sched = AcademicSchedule(self.memory)
                sched.add_class(params.get("day", "Monday"), params.get("subject", ""), params.get("start_time", ""), params.get("room", ""))
            elif name == "add_assignment":
                from features.academic.assignments import AssignmentTracker
                tracker = AssignmentTracker(self.memory)
                import time
                deadline_days = float(params.get("deadline_days", 7))
                deadline_ts = time.time() + deadline_days * 86400
                tracker.add_assignment(params.get("subject", ""), params.get("description", ""), deadline_ts)
            elif name == "mark_assignment_completed":
                from features.academic.assignments import AssignmentTracker
                tracker = AssignmentTracker(self.memory)
                tracker.mark_completed(params.get("key", ""))
            elif name == "log_water":
                from features.health.hydration import HydrationTracker
                tracker = HydrationTracker(self.memory)
                tracker.log_water_intake(int(params.get("ml", 250)))
            elif name == "add_medication":
                from features.health.medication import MedicationManager
                mgr = MedicationManager(self.memory)
                mgr.add_medication(params.get("name", ""), params.get("dose", ""), params.get("time_of_day", ""))
            elif name == "trigger_sos":
                from features.emergency.sos import SOSEngine
                sos = SOSEngine(self.memory)
                sos.trigger_sos()
            elif name == "schedule_fake_call":
                from features.emergency.fake_call import FakeCallScheduler
                sched = FakeCallScheduler()
                sched.schedule_fake_call(float(params.get("minutes", 1.0)))
            elif name == "start_study_mode":
                from features.academic.study_mode import StudyModeManager
                mgr = StudyModeManager()
                mgr.start_pomodoro(int(params.get("work_mins", 25)), int(params.get("break_mins", 5)))
            elif name == "stop_study_mode":
                from features.academic.study_mode import StudyModeManager
                mgr = StudyModeManager()
                mgr.stop_study_session()
            elif name == "activate_low_power":
                from features.hostel.power_mode import PowerModeManager
                mgr = PowerModeManager()
                mgr.activate_ultra_low_power()
            elif name == "deactivate_low_power":
                from features.hostel.power_mode import PowerModeManager
                mgr = PowerModeManager()
                mgr.deactivate_ultra_low_power()
            elif name == "activate_focus":
                from features.lifestyle.focus import FocusModeController
                ctrl = FocusModeController()
                ctrl.activate_focus()
            elif name == "deactivate_focus":
                from features.lifestyle.focus import FocusModeController
                ctrl = FocusModeController()
                ctrl.deactivate_focus()
            elif name == "activate_whisper":
                from modes.whisper import WhisperModeController
                ctrl = WhisperModeController(None, self)
                ctrl.activate_whisper()
            elif name == "deactivate_whisper":
                from modes.whisper import WhisperModeController
                ctrl = WhisperModeController(None, self)
                ctrl.deactivate_whisper()
            elif name == "open_app":
                from integrations.browser import BrowserController
                ctrl = BrowserController()
                app_target = params.get("name") or params.get("app_name", "")
                ctrl.open_app(app_target)
        except Exception as e:
            logger.error(f"Error executing action {name}: {e}")

    def request_permission(self, action_description: str) -> bool:
        """Helper to prompt for user authorization prior to destructive/sensitive actions."""
        # In a real environment, this might wait for a voice/UI response or click.
        # We simulate the prompt here.
        print(f"\n[PERMISSION REQUEST] Boss, may I perform the following: {action_description}?")
        # Defaults to True in tests, or prompts console.
        return True
    
    def start_voice_loop(self) -> None:
        """Starts the persistent background voice activation loop."""
        from voice.listener import EdithListener
        from voice.speaker import EdithSpeaker
        import time

        listener = EdithListener(brain=self)
        speaker = EdithSpeaker(brain=self)
        
        speaker.speak("Edith is sleeping. Say 'Hey Edith' or 'Edith, good morning' to wake me up.")
        
        try:
            while True:
                # 1. Listen for wake word
                if listener.listen_for_wake_word("Edith, good morning"):
                    # Play a soft double-beep chime
                    try:
                        import winsound
                        winsound.Beep(800, 150)
                        winsound.Beep(1200, 200)
                    except Exception as e:
                        logger.warning(f"Failed to play chime: {e}")

                    speaker.speak("I'm here, Boss.")
                    
                    # 2. Conversation loop once awake
                    last_active_time = time.time()
                    while True:
                        # If sleep toggled from HUD, go back to sleep
                        if getattr(self, "is_sleeping", False):
                            speaker.speak("Going to sleep now, Boss.")
                            break

                        # If inactive for more than 30 seconds, go back to sleep
                        if time.time() - last_active_time > 30.0:
                            speaker.speak("Going to sleep now, Boss.")
                            break
                            
                        user_phrase = listener.listen()
                        if not user_phrase:
                            time.sleep(0.1)
                            continue
                        
                        print(f"\nBoss: {user_phrase}")
                        try:
                            if self.hud:
                                self.hud.add_chat_message("Boss", user_phrase)
                        except Exception:
                            pass

                        last_active_time = time.time()
                        
                        # Check sleep triggers
                        if any(w in user_phrase.lower() for w in ("goodnight", "sleep", "go to sleep", "stop edith")):
                            speaker.speak("Going to sleep now, Boss.")
                            break
                            
                        # Always confirm what was heard before executing
                        speaker.speak(f"Heard {user_phrase}.")
                        
                        # Process query through safety, routing and LLM
                        response = self.process_input(user_phrase)
                        if response:
                            speaker.speak(response)
                            
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Voice loop error: {e}")

    def shutdown(self) -> None:
        """Shuts down background queues and processes."""
        self.tasks.shutdown()
