import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fastapi import APIRouter, HTTPException

from config import BROKER_HOST, BROKER_PORT, BROKER_USERNAME, BROKER_PASSWORD
from models import StartBotAction, StopBotAction, ImportStrategyAction
from services.bots_orchestrator import BotsManager

# Initialize the scheduler
scheduler = AsyncIOScheduler()
router = APIRouter(tags=["Manage Broker Messages"])
bots_manager = BotsManager(broker_host=BROKER_HOST, broker_port=BROKER_PORT, broker_username=BROKER_USERNAME,
                           broker_password=BROKER_PASSWORD)


def update_active_bots():
    bots_manager.update_active_bots()


@router.on_event("startup")
async def startup_event():
    # Add the job to the scheduler
    scheduler.add_job(update_active_bots, 'interval', seconds=10)
    scheduler.start()


@router.on_event("shutdown")
async def shutdown_event():
    # Shutdown the scheduler on application exit
    scheduler.shutdown()


@router.get("/get-active-bots-status")
def get_active_bots_status():
    """Returns the cached status of all active bots."""
    if not bots_manager.active_bots:
        raise HTTPException(status_code=404, detail="No active bots found")
    return {"status": "success", "data": bots_manager.get_all_bots_status()}


@router.get("/get-bot-status/{bot_name}")
def get_bot_status(bot_name: str):
    response = bots_manager.get_bot_status(bot_name)
    if not response:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {
        "status": "success",
        "data": response
    }


@router.get("/get-bot-history/{bot_name}")
def get_bot_history(bot_name: str):
    response = bots_manager.get_bot_history(bot_name)
    return {"status": "success", "response": response}


@router.post("/start-bot")
def start_bot(action: StartBotAction):
    response = bots_manager.start_bot(action.bot_name, log_level=action.log_level, script=action.script,
                                      conf=action.conf, async_backend=action.async_backend)
    return {"status": "success", "response": response}


@router.post("/stop-bot")
def stop_bot(action: StopBotAction):
    response = bots_manager.stop_bot(action.bot_name, skip_order_cancellation=action.skip_order_cancellation,
                                     async_backend=action.async_backend)
    return {"status": "success", "response": response}


@router.post("/import-strategy")
def import_strategy(action: ImportStrategyAction):
    response = bots_manager.import_strategy_for_bot(action.bot_name, action.strategy)
    return {"status": "success", "response": response}
