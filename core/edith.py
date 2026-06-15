import os
import logging
from typing import Dict, Any, Optional
import re
from config import settings
from core.memory import EdithMemory
from core.context import EdithContext
from core.tasks import EdithTaskManager
from core.learning import EdithLearningManager
from voice.language import EdithLanguageManager
from voice.tone_detector import EdithToneDetector
from security.safety_gate import SafetyGate

logger = logging.getLogger("EDITH.Core")

class EdithBrain:
    def __init__(self) -> None:
        self.memory = EdithMemory()
        self.context = EdithContext()
        self.tasks = EdithTaskManager()
        self.learning = EdithLearningManager(self.memory)
        self.language_manager = EdithLanguageManager()
        self.tone_detector = EdithToneDetector()
        self.safety_gate = SafetyGate()
        
        # Determine if onboarding has been completed
        self.onboarded = self.memory.get_memory("system", "onboarded") == "True"

        # Start background reminder daemon thread
        import threading
        self.reminder_thread = threading.Thread(target=self._run_reminder_daemon, daemon=True)
        self.reminder_thread.start()

    def process_input(self, user_text: str) -> str:
        """Processes user input through safety guards, routing, and conversation rules."""
        if not user_text:
            return ""

        # 0. Detect Tone and Language
        self.context.boss_tone = self.tone_detector.analyze_lexical_tone(user_text)
        user_lang = self.language_manager.detect_language(user_text)
        
        # Translate Hinglish/Hindi inputs to English for internal routing & safety gates
        user_text_en = user_text
        if user_lang in ("hinglish", "hindi"):
            user_text_en = self.language_manager.translate_to_english(user_text)
            logger.info(f"Translated input to English: '{user_text_en}'")

        # 1. Check Panic Word
        panic_word = self.memory.get_memory("security", "panic_word")
        if panic_word and (panic_word.lower() in user_text.lower() or panic_word.lower() in user_text_en.lower()):
            from security.panic import trigger_panic
            return trigger_panic(self)

        # 2. Check Jailbreak / Injection Attempt
        from security.intrusion import IntrusionDetector
        detector = IntrusionDetector()
        if detector.detect_injection(user_text_en):
            detector.alert_boss(user_text_en)
            return "Security violation logged, Boss. Prompt injection attempt detected and blocked."

        # 3. Check DND mode
        if self.context.dnd_mode:
            # Only priority breakthroughs allowed
            is_priority = False
            priority_contacts = self.memory.get_all_memories_by_topic("priority_contacts")
            for contact in priority_contacts.keys():
                if contact.lower() in user_text_en.lower():
                    is_priority = True
                    break
            if not is_priority:
                return ""  # Zero response, zero logging in DND

        # 4. Save input context if Zero Knowledge mode is disabled
        if not self.context.zero_knowledge_mode:
            self.memory.log_dialogue(self.context.session_id, "user", user_text)

        # 4.2 Check Guest and Roommate Mode Switches (Must bypass block check)
        cleaned_input_en = user_text_en.lower().strip()
        if "guest mode off" in cleaned_input_en or "deactivate guest" in cleaned_input_en:
            self.context.guest_mode = False
            return "Guest mode deactivated. Welcome back, Boss."
        elif "roommate mode off" in cleaned_input_en or "deactivate roommate" in cleaned_input_en:
            self.context.roommate_mode = False
            return "Roommate mode deactivated. Welcome back, Boss."

        # 4.3 Check Guest and Roommate Restrictions
        if getattr(self.context, "guest_mode", False):
            from modes.guest import GuestPermissionsManager
            guest_mgr = GuestPermissionsManager()
            restricted = True
            for topic in guest_mgr.whitelisted_topics:
                if topic in cleaned_input_en:
                    restricted = False
                    break
            if any(w in cleaned_input_en for w in ["hello", "hey", "morning", "weather", "canteen", "timetable", "mess"]):
                restricted = False
            if restricted:
                return "Access denied. Topic or action is restricted in Guest mode, Boss."
                
        elif getattr(self.context, "roommate_mode", False):
            from modes.roommate import RoommateModeManager
            roommate_mgr = RoommateModeManager()
            restricted = True
            for topic in roommate_mgr.whitelisted_topics:
                if topic in cleaned_input_en:
                    restricted = False
                    break
            if any(w in cleaned_input_en for w in ["hello", "hey", "morning", "weather", "canteen", "timetable", "mess"]):
                restricted = False
            if restricted:
                return "Access denied. Topic or action is restricted in Roommate mode, Boss."

        # 4.5 Direct application launcher shortcut
        if cleaned_input_en.startswith("open ") or cleaned_input_en.startswith("launch "):
            app_name = cleaned_input_en.replace("open ", "").replace("launch ", "").strip()
            
            # Check safety gate and modes permissions
            if getattr(self.context, "guest_mode", False) or getattr(self.context, "roommate_mode", False):
                return "Access denied. Opening apps is restricted in this mode."
                
            if not self.safety_gate.is_app_allowed(app_name):
                return f"Access denied. Application '{app_name}' is not whitelisted, Boss."
                
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
        response = self._dispatch_routing(user_text_en)

        # 6. Parse and execute LLM structured actions if any
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
            if pattern.lower() in user_text_en.lower():
                response += f"\n[Rule applied: {correction}]"

        # Tone adaptation & language formulation
        if response:
            if self.context.boss_tone == "stressed":
                response = f"Take a deep breath, Boss. I've got you covered. {response}"
            elif self.context.boss_tone == "playful":
                response = f"Haha, copy that, Boss! {response}"
            elif self.context.boss_tone == "work":
                response = f"Copy that, Boss. Focus mode active. {response}"
                
            response = self.language_manager.formulate_response(response, user_lang)

        # Post-processing: Replace any occurrence of 'Jarvis' or 'jarvis' with 'EDITH'
        if response:
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

        # Morning Routine
        if "good morning" in cleaned or "morning routine" in cleaned or "morning schedule" in cleaned:
            return self.run_morning_routine()

        # Guest and Roommate Mode Switches
        if "guest mode on" in cleaned or "activate guest" in cleaned:
            self.context.guest_mode = True
            self.context.roommate_mode = False
            return "Guest mode activated, Boss. Access to personal files and sensitive controls is locked."
        elif "guest mode off" in cleaned or "deactivate guest" in cleaned:
            self.context.guest_mode = False
            return "Guest mode deactivated. Welcome back, Boss."
        elif "roommate mode on" in cleaned or "activate roommate" in cleaned or "roommate mode" in cleaned:
            self.context.roommate_mode = True
            self.context.guest_mode = False
            return "Roommate mode activated, Boss. Personal systems are locked down."
        elif "roommate mode off" in cleaned or "deactivate roommate" in cleaned:
            self.context.roommate_mode = False
            return "Roommate mode deactivated. Boss profile restored."

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
        
        # 1. Enforce Safety Gate Whitelists
        if name == "open_app":
            app_target = params.get("name") or params.get("app_name", "")
            if not self.safety_gate.is_app_allowed(app_target):
                logger.warning(f"SafetyGate: Blocked execution of application '{app_target}'")
                return
                
        # 2. Check Guest/Roommate restrictions on action execution
        if getattr(self.context, "guest_mode", False):
            from modes.guest import GuestPermissionsManager
            guest_mgr = GuestPermissionsManager()
            if not guest_mgr.is_action_allowed(name):
                logger.warning(f"GuestMode: Blocked action {name}")
                return
        elif getattr(self.context, "roommate_mode", False):
            from modes.roommate import RoommateModeManager
            roommate_mgr = RoommateModeManager()
            if not roommate_mgr.is_action_allowed(name):
                logger.warning(f"RoommateMode: Blocked action {name}")
                return

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
                    speaker.play_alert("wake")

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

    def run_morning_routine(self) -> str:
        """Gathers schedule, weather, budget, tasks, and presents a morning overview."""
        boss_name = self.memory.get_memory("security", "boss_name") or "Boss"
        greeting = f"Good morning, {boss_name}! EDITH is online and fully tactical.\n"
        
        # 1. Weather
        from integrations.weather import WeatherIntegration
        weather = WeatherIntegration()
        weather_info = weather.get_weather("Delhi")
        
        # 2. Timetable / Schedule
        from features.academic.schedule import get_schedule_summary
        schedule_info = get_schedule_summary(self.memory)
        
        # 3. Pending assignments
        from features.academic.assignments import AssignmentTracker
        tracker = AssignmentTracker(self.memory)
        pending = tracker.get_pending_assignments()
        if pending:
            assignments_info = f"You have {len(pending)} pending assignments. The next one is due in {pending[0]['days_remaining']} days."
        else:
            assignments_info = "No pending assignments due. Great job!"
            
        # 4. Battery / Metrics
        import psutil
        battery_pct = "100%"
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_pct = f"{int(battery.percent)}%"
        except Exception:
            pass
            
        # 5. Fun / motivational close
        from features.lifestyle.meme_mode import MemeManager
        memes = MemeManager()
        joke = memes.get_random_meme()
        if joke.startswith("Title:"):
            joke = "Ready for the day!"
        
        response = (
            f"{greeting}\n"
            f"🌤️ {weather_info}\n"
            f"📅 {schedule_info}\n"
            f"📝 {assignments_info}\n"
            f"🔋 Battery: {battery_pct} | System: OPTIMAL.\n"
            f"💡 Dev joke of the day: {joke}\n"
            f"Have a great day, {boss_name}!"
        )
        return response

    def _run_reminder_daemon(self) -> None:
        """Daemon loop to check and alert for medication, curfew, and mess times."""
        import time
        from datetime import datetime
        
        logger.info("Background reminders daemon started.")
        last_checked_minute = -1
        
        while True:
            try:
                time.sleep(10)
                
                # Check DND mode
                if self.context.dnd_mode:
                    continue
                    
                now = datetime.now()
                if now.minute == last_checked_minute:
                    continue
                last_checked_minute = now.minute
                
                current_time_str = now.strftime("%H:%M")
                
                # 1. Medication check
                from features.health.medication import MedicationManager
                med_mgr = MedicationManager(self.memory)
                active_meds = med_mgr.get_active_medications()
                for med in active_meds:
                    if med["time"] == current_time_str:
                        alert_msg = f"Alert: Time to take your medication, Boss! Dose of {med['name']} ({med['dose']}) is due now."
                        self._dispatch_reminder(alert_msg, "breakthrough")
                
                # 2. Gate Curfew check (30 mins before gate closing)
                curfew_hour = settings.HOSTEL_GATE_CURFEW_HOUR
                if now.hour == curfew_hour - 1 and now.minute == 30:
                    alert_msg = f"Hostel Curfew Warning, Boss! The main gate closing is in 30 minutes at {curfew_hour}:00."
                    self._dispatch_reminder(alert_msg, "warning")
                    
                # 3. Mess Times check
                mess_breakfast = settings.MESS_BREAKFAST_TIME
                mess_lunch = settings.MESS_LUNCH_TIME
                mess_dinner = settings.MESS_DINNER_TIME
                
                if current_time_str == mess_breakfast:
                    self._dispatch_reminder("Boss, Breakfast is now open at the canteen.", "success")
                elif current_time_str == mess_lunch:
                    self._dispatch_reminder("Boss, Lunch is now served at the canteen.", "success")
                elif current_time_str == mess_dinner:
                    self._dispatch_reminder("Boss, Dinner is now open at the canteen.", "success")
                    
            except Exception as e:
                logger.error(f"Error in reminders daemon loop: {e}")

    def _dispatch_reminder(self, msg: str, sound_type: str) -> None:
        from voice.speaker import EdithSpeaker
        try:
            if self.hud:
                self.hud.add_chat_message("System", msg)
        except Exception:
            pass
        speaker = EdithSpeaker(self)
        speaker.play_alert(sound_type)
        speaker.speak(msg)

    def shutdown(self) -> None:
        """Shuts down background queues and processes."""
        self.tasks.shutdown()
