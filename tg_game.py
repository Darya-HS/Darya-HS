from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import ApplicationBuilder
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
import traceback
import logging

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(message)s")


def get_start_button():
    keyboard = [
        [InlineKeyboardButton("Start Game", callback_data='start_game')]
    ]
    return InlineKeyboardMarkup(keyboard)

class Unit:
    def __init__(self, name, health, sdamage, srecover, maxRecover):
        self.name = name
        self.health = health
        self.sdamage = sdamage
        self.srecover = srecover
        self.maxHealth = health
        self.maxBlock = sdamage
        self.action = "start"
        self.outDam = 0
        self.maxRecover = maxRecover
        self.recCounter = 0

    def toAttack(self):
        if self.isAlive():
            self.setAction("attack")
            self.outDam = self.sdamage
        return

    def toBlockAttack(self, dam):
        self.health = max(0.3, round(self.health - (dam - self.maxBlock), 1))
        self.setAction("block")
        self.maxBlock = max(0, self.maxBlock - 0.1)
        self.outDam = 0

    def toHeel(self):
        if self.isAlive():
            rec = round(self.health + self.srecover, 1)
            if rec < self.maxHealth / 2:
                self.health = round(rec, 1)
                self.setAction("recover")
                self.recCounter += 1
            elif rec > self.maxHealth / 2 > self.health:
                self.health = round(self.maxHealth / 2, 1)
                self.setAction("recover")
                self.recCounter += 1
            else:
                self.health = self.health
            self.outDam = 0
            return

    def isAlive(self):
        if self.health > 0.3:
            return True
        
        self.setAction("die")
        self.outDam = 0
        return False

    def getDamaged(self, dam):
        self.health = max(0.3, round(self.health - dam, 1))
        return

    def setName(self, name):
        self.name = name
        return
    def getName(self):
        return self.name

    def setHealth(self, health):
        self.health = health
        return
    def getHealth(self):
        return self.health

    def setSDamage(self, sdamage):
        self.sdamage = sdamage
        return

    def getSDamage(self):
        return self.sdamage

    def setSRecover(self, srecover):
        self.srecover = srecover
        return
    def getSRecover(self):
        return  self.srecover

    def setMaxHealth(self, maxHealth):
        self.maxHealth = maxHealth
        return

    def getMaxHealth(self):
        return self.maxHealth

    def setMaxBlock(self, maxBlock):
        self.maxBlock = maxBlock
        return
    def getMaxBlock(self):
        return self.maxBlock

    def setAction(self, action):
        self.action = action
        return
    def getAction(self):
        return self.action
    def getRecCounter(self):
        return self.recCounter
    def setRecCounter(self, recCounter):
        self.recCounter = recCounter
        return
    def getMaxRec(self):
        return self.maxRecover
    def setMaxRec(self, maxRec):
        self.maxRecover = maxRec
        return

class Player(Unit):
    def Control(self, key, opponent):
        dam = opponent.outDam
        if self.isAlive():
            if key == "1":
                self.getDamaged(dam)
                self.toAttack()
                # Stop if the opponent is dead
                if not opponent.isAlive():
                    opponent.setAction("die")
                    opponent.outDam = 0
                    return
            elif key == "2":
                if opponent.getAction() == "attack":  # Block only if bot attacked
                    self.toBlockAttack(dam)
                else:
                    print("No attack to block. Block action skipped!")
            elif key == "3":
                self.getDamaged(dam)
                self.toHeel()
        print(self.name, self.getAction())
        return
                
class Bot(Unit):
    def __init__(self, name, health, sdamage, srecover, maxRecover, transition_matrix):
        super().__init__(name, health, sdamage, srecover, maxRecover)
        self.transition_matrix = transition_matrix

    def set_transition_matrix(self, matrix):
        self.transition_matrix = matrix

    def play(self, opponent):
        dam = opponent.outDam
        if self.getAction() == "start":
            self.setAction("attack")

        if self.isAlive():
            # Determine probabilities based on health and opponent's state
            probabilities = self.determine_probabilities(opponent)

            # Choose action based on calculated probabilities
            actions = ["attack", "block", "recover"]
            action = random.choices(actions, weights=probabilities)[0]

            if action == "attack":
                self.getDamaged(dam)
                self.toAttack()
                if not opponent.isAlive():
                    opponent.setAction("die")
                    opponent.outDam = 0
                    return
            elif action == "block":
                if opponent.getAction() == "attack":  # Block only if the opponent attacked
                    self.toBlockAttack(dam)
            else:
                self.getDamaged(dam)  # Take damage while recovering
                self.toHeel()

        print(self.getName(), self.getAction())
        return

    def determine_probabilities(self, opponent):
        """
        Calculate the probabilities for the bot's actions based on health,
        opponent's action, and current bot action
        """
        if opponent.getAction() == "attack":
            if self.getHealth() < self.getMaxHealth() / 2 and self.getRecCounter() <= self.getMaxRec():
                if self.getAction() == "attack":
                    return self.transition_matrix[0]
                elif self.getAction() == "block":
                    return self.transition_matrix[1]
                else:
                    return self.transition_matrix[2]
            else:
                if self.getAction() == "attack":
                    return self.transition_matrix[3]
                elif self.getAction() == "block":
                    return self.transition_matrix[4]
                else:
                    return self.transition_matrix[5]
        else:
            if self.getHealth() < self.getMaxHealth() / 2:
                if self.getAction() == "attack":
                    return self.transition_matrix[6]
                elif self.getAction() == "block":
                    return self.transition_matrix[7]
                else:
                    return self.transition_matrix[8]
            else:
                return self.transition_matrix[9]

transition_matrix_E = [
    [0.6, 0.2, 0.2],
    [0.7, 0.1, 0.2],
    [0.9, 0.05, 0.05],
    [0.6, 0.4, 0],
    [0.7, 0.3, 0],
    [0.9, 0.1, 0],
    [0.6, 0, 0.4],
    [0.7, 0, 0.3],
    [0.9, 0, 0.1],
    [1, 0, 0]
]

transition_matrix_M = [
    [0.4, 0.3, 0.3],
    [0.5, 0.2, 0.3],
    [0.8, 0.1, 0.1],
    [0.5, 0.5, 0],
    [0.6, 0.4, 0],
    [0.8, 0.2, 0],
    [0.5, 0, 0.5],
    [0.6, 0, 0.4],
    [0.8, 0, 0.2],
    [1, 0, 0]
]

game_states = {}

async def start_game(update: Update, context: CallbackContext) -> None:
    if update.message:
        user_id = update.message.chat_id
        
        game_states[user_id] = {
            "player": None,
            "bot": None,
            "turn": None,
            "game_over": False,
            "turn_completed": False,
        }

        keyboard = [
            [InlineKeyboardButton("Easy", callback_data="easy")],
            [InlineKeyboardButton("Medium", callback_data="medium")],
            [InlineKeyboardButton("Hard", callback_data="hard")],
        ]
        await update.message.reply_text(
            "Welcome! Choose a difficulty level:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def set_difficulty(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id

    player = Player(name="Player", health=10, sdamage=1, srecover=2, maxRecover=5)
    bot = Bot(name="Bot", health=10, sdamage=1, srecover=1, maxRecover=5, transition_matrix=None)

    game_states[user_id]["player"] = player
    game_states[user_id]["bot"] = bot
    game_states[user_id]["turn"] = "player"

    if query.data == "easy":
        bot.set_transition_matrix(transition_matrix_E)
    elif query.data == "medium":
        bot.set_transition_matrix(transition_matrix_M)
    elif query.data == "hard":
        bot.set_transition_matrix(transition_matrix_M)
        bot.setSRecover(2)

    await query.edit_message_text("Difficulty set! Let the game begin!")
    await send_game_status(query, context)

def determine_player_choices(player, bot):
    """
    Determine valid actions for the player based on health, recovery count,
    and the bot's current action.
    """
    valid_actions = []

    # Attack is always valid
    valid_actions.append("attack")

    # Block is only valid if the bot is attacking
    if bot.getAction() == "attack":
        valid_actions.append("block")

    # Recover is only valid if the player is below 50% health and has recovery attempts left
    if player.getHealth() < player.getMaxHealth() / 2 and player.getRecCounter() < player.getMaxRec():
        valid_actions.append("recover")

    return valid_actions

async def handle_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id

    state = game_states[user_id]
    if state.get("game_over", False):
        return

    player = state["player"]
    bot = state["bot"]

    valid_actions = determine_player_choices(player, bot)

    action = query.data
    if action not in valid_actions:
        await query.message.reply_text("Invalid choice. Please select a valid action.")
        return

    if action == "attack":
        player.Control("1", bot)
        if not bot.isAlive():
            state["game_over"] = True
            await query.edit_message_text("You win!")
            return
    elif action == "block":
        player.Control("2", bot)
    elif action == "recover":
        player.Control("3", bot)

    if not state.get("game_over", False):
        state["turn"] = "bot"
        await bot_turn_simulation(query, context)

async def send_game_action(query: Update, context: CallbackContext, action: str) -> None:
    user_id = query.message.chat_id
    state = game_states[user_id]

    if state.get("game_over", False):
        return

    await query.message.reply_text(action)

async def send_game_status(query: Update, context: CallbackContext) -> None:
    user_id = query.message.chat_id
    state = game_states[user_id]

    if state.get("game_over", False):
        return

    player = state["player"]
    bot = state["bot"]
    turn = state.get("turn", "player")

    status = (
        f"Bot health: {bot.getHealth()} / {bot.getMaxHealth()}\n"
        f"Player health: {player.getHealth()} / {player.getMaxHealth()}\n"
        f"Turn: {'Player' if turn == 'player' else 'Bot'}\n\n"
    )

    if turn == "player":
        valid_actions = determine_player_choices(player, bot)
        keyboard = []

        if "attack" in valid_actions:
            keyboard.append([InlineKeyboardButton("Attack", callback_data="attack")])
        if "block" in valid_actions:
            keyboard.append([InlineKeyboardButton("Block", callback_data="block")])
        if "recover" in valid_actions:
            keyboard.append([InlineKeyboardButton("Recover", callback_data="recover")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=user_id, text=status, reply_markup=reply_markup)

async def bot_turn_simulation(query: Update, context: CallbackContext) -> None:
    user_id = query.message.chat_id
    state = game_states[user_id]

    if state.get("game_over", False) or state.get("turn_completed", False):
        return

    bot = state["bot"]
    player = state["player"]

    bot.play(player)
    action_message = f"Bot {bot.getAction()}s!"

    if not player.isAlive():
        state["game_over"] = True
        await query.edit_message_text("Player dies! Computer wins!")
        return

    if not state.get("game_over", False):
        await send_game_action(query, context, action_message)

    state["turn_completed"] = False
    state["turn"] = "player"
    await send_game_status(query, context)

async def error_handler(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    logging.error("".join(traceback.format_exception(None, context.error, context.error.__traceback__)))


def main():
    application = ApplicationBuilder().token("7918711540:AAF85M7_3HZHGA0Po_CUOza4xWtdZDUtM6c").build()

    application.add_handler(CommandHandler("start", start_game))
    application.add_handler(CallbackQueryHandler(start_game, pattern='^start_game$'))
    application.add_handler(CallbackQueryHandler(set_difficulty, pattern="^(easy|medium|hard)$"))
    application.add_handler(CallbackQueryHandler(handle_action, pattern="^(attack|block|recover)$"))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    main()