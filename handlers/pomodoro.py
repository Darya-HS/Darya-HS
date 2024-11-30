
from telegram import Update
from telegram.ext import ContextTypes
from datetime import timedelta

async def start_pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        args = context.args
        work_duration = int(args[0]) if len(args) > 0 else 25  # Default: 25 minutes work
        break_duration = int(args[1]) if len(args) > 1 else 5   # Default: 5 minutes break
        cycles = int(args[2]) if len(args) > 2 else 1           # Default: 1 cycle

        # Schedule the first work period
        context.job_queue.run_once(
            work_period,
            when=timedelta(minutes=work_duration),
            data={
                "chat_id": update.message.chat_id,
                "work_duration": work_duration,
                "break_duration": break_duration,
                "remaining_cycles": cycles,
            },
            name=f"pomodoro_{update.message.chat_id}"  # Unique name for Pomodoro job
        )

        await update.message.reply_text(
            f"Pomodoro started! Focus for {work_duration} minutes. 🍅 Total cycles: {cycles}"
        )
    except ValueError:
        await update.message.reply_text("Invalid input. Use /pomodoro <work_duration> <break_duration> <cycles>")

async def work_period(context: ContextTypes.DEFAULT_TYPE) -> None:
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    break_duration = job_data["break_duration"]
    remaining_cycles = job_data["remaining_cycles"]

    # Notify the user that the work period is over
    await context.bot.send_message(chat_id=chat_id, text="This cycle is complete! Take your break ☕")

    # Schedule the break period
    context.job_queue.run_once(
        break_period,
        when=timedelta(minutes=break_duration),
        data={
            "chat_id": chat_id,
            "work_duration": job_data["work_duration"],
            "break_duration": break_duration,
            "remaining_cycles": remaining_cycles,
        },
        name=f"pomodoro_{chat_id}"
    )

async def break_period(context: ContextTypes.DEFAULT_TYPE) -> None:
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    work_duration = job_data["work_duration"]
    remaining_cycles = job_data["remaining_cycles"] - 1  # Decrease remaining cycles

    if remaining_cycles > 0:
        # Notify the user that the break is over
        await context.bot.send_message(chat_id=chat_id, text="Break time is over! Time to get back to work 💪")

        # Schedule the next work period
        context.job_queue.run_once(
            work_period,
            when=timedelta(minutes=work_duration),
            data={
                "chat_id": chat_id,
                "work_duration": work_duration,
                "break_duration": job_data["break_duration"],
                "remaining_cycles": remaining_cycles,
            },
            name=f"pomodoro_{chat_id}"
        )
    else:
        # Notify the user that the Pomodoro session is complete
        await context.bot.send_message(chat_id=chat_id, text="Your Pomodoro session is complete! 🎉")

async def cancel_pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_prefix = f"pomodoro_{chat_id}"

    # Find and cancel only Pomodoro jobs
    current_jobs = context.job_queue.jobs()
    for job in current_jobs:
        if job.name and job.name.startswith(job_prefix):
            job.schedule_removal()

    await update.message.reply_text("Pomodoro session canceled. You can start again with /pomodoro or customize it with /pomodoro <work_duration> <break_duration> <cycles>!")