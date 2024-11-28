# Study Planner Bot 🤖

**Study Planner Bot** is a feature-rich Telegram bot designed to help students plan and manage their studies effectively. It allows users to create personalized profiles, set goals, track progress, manage flashcards, set reminders, have pomodoro sessions, access their university website easily, and just have fun studying!

## Table of Contents

- [Features](#features)
- [Commands](#commands)
- [File Structure](#file-structure)
- [Technologies Used](#technologies-used)

---

## Features

1. **User Profile Management**  
   - Register a profile with a username and timezone  
   - View, update, or delete profile details

2. **Study Goal Management**  
   - Add goals by specifying subject, name (midterm, project or anything else), and target hours  
   - Update, delete, or log hours for each goal  
   - View progress and completion percentage of goals

3. **Time Management**  
   - Set daily reminders to help you build healthy study habits 
   - Cancel reminders when you get tired of them

4. **Pomodoro Timer**  
   - Start Pomodoro sessions to improve focus. This session is by default 1 cycle of studying (25 minutes) + break (5 minutes), but you can set whatever time periods you like and however many cycles you wish to study. 
   - Cancel the sessions if you feel overwhelmed

5. **Flashcard Management**  
   - Create, view, practice, and delete flashcards (questions + answers)

6. **Quick Access to Websites**  
   - Save your university website for fast access and open it directly via the bot

7. **Cancel Ongoing Actions**  
   - Easily cancel any active commands

---

## Commands
This is the list of all the available command in the bot with their detailed description

| Command               | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **/start**            | Start the bot and see the welcome message                                 |
| **/register**         | Register a new user profile                                               |
| **/view_profile**     | View your current profile                                                 |
| **/update_profile**   | Update your username, timezone, or goals                                  |
| **/set_goal**         | Create a new study goal                                                   |
| **/progress**         | View the progress of your study goals                                     |
| **/log_time**         | Log hours for an existing goal                                            |
| **/set_reminder**     | Set a daily reminder for studying                                         |
| **/cancel_reminder**  | Cancel your active reminder                                               |
| **/add_flashcard**    | Add a new flashcard for study                                             |
| **/view_flashcards**  | View all your flashcards                                                  |
| **/practice_flashcards** | Practice your flashcards                                               |
| **/delete_flashcard** | Delete a specific flashcard                                               |
| **/set_site**         | Save a website for quick access                                           |
| **/clean_site**         | Delete the website you set                                              |
| **/site**             | Open the saved website                                                   |
| **/pomodoro**         | Start a Pomodoro session                                                 |
| **/cancel_pomodoro**  | Cancel the current Pomodoro session                                       |
| **/help**             | See the full list of available commands (also available as a button)      |
| **/cancel**           | Cancel any ongoing action                                                |

---

## File Structure

Darya_HS/

─ handlers/                    Contains modular handlers for bot features
    ─ general.py               General commands like /start, /help, /cancel
    ─ profile.py               Profile management handlers
    ─ goals.py                 Goal-related handlers
    ─ flashcards.py            Flashcard management handlers
    ─ reminder.py              Reminder-related handlers
    ─ pomodoro.py              Pomodoro session handlers
    ─ site.py                  Website-related handlers

─ utils/                       Utility files
    ─ data.py                  JSON-based data management
    ─ keyboards.py             Keyboard utilities for inline/reply buttons

─ profiles.json                JSON file to store user data (is not present by default, will appear after the first run)
─ main.py                      Entry point for the bot
─ README.md                    Project documentation
─ states.py                    Storing of states as a single point of truth for all handlers

---

## Features
- **Python**: Core programming language for development
- **Python-Telegram-Bot**: Library for creating Telegram bots
- **JSON**: Storage for user data to avoid reregistering in case of bot failure
- **Pytz**: Timezone management for reminders