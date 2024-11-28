# State identifiers for conversation flows

# Registration and profile management states
USERNAME, PREFERENCES, GOALS, SELECT_FIELD, UPDATE_FIELD = range(5)

# Time management and reminders
REMINDER_TIME, LOG_TIME_SELECTION, LOG_TIME_HOURS, SET_SITE_URL = range(5, 9)

# Goals and progress management
SET_GOAL_SUBJECT, SET_GOAL_NAME, SET_GOAL_HOURS = range(9, 12)
UPDATE_PROFILE, UPDATE_USERNAME, UPDATE_TIMEZONE, UPDATE_GOAL_SELECTION, UPDATE_GOAL_ACTION, EDIT_GOAL_HOURS = range(12, 18)

# Flashcard management
ADD_QUESTION, ADD_ANSWER, VIEW_FLASHCARD, DELETE_FLASHCARD, PRACTICE_FLASHCARD = range(18, 23)