#starts nexa->load config->init db->create event bus->subs orch->pub test cmd->ping skill exec->log res
import asyncio
import logging

from nexa.config import get_config
from nexa.db import get_connection
from nexa.event_bus import get_event_bus
from nexa.skills.ping import PingSkill

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("nexa")

async def handle_command_received(payload: dict) -> None:
    """
    This is a stand-in for the real orchestrator 
    """
    text = payload.get("text", "")
    log.info(f"Command received: '{text}'")

    skill = PingSkill()
    result = await skill.execute(params={}, context={})

    log.info(f"Skill '{skill.name}' responded: {result.spoken_response}")

async def main():
    cfg = get_config()
    log.info(f"Nexa starting up for {cfg.user_name}")
    log.info(f"Data directory: {cfg.data_dir}")

    # Initialize DB (creates the file + tables on first run)
    conn = get_connection()
    log.info(f"Database ready at {cfg.db_path}")
    conn.close()

    # Set up the event bus and subscribe our (fake, for now) orchestrator
    bus = get_event_bus()
    bus.subscribe("command_received", handle_command_received)

    log.info("Nexa is up. Simulating one command since we have no voice input yet...")
    # For now, we fire one manually to prove the pipeline works.
    await bus.publish("command_received", {"text": "hey nexa are you there"})

    log.info("Phase 0 pipeline verified end-to-end. Ready for Phase 1 (voice).")

if __name__ == "__main__":
    asyncio.run(main())
