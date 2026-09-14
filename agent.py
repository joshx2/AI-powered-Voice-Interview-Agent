from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RoomInputOptions,
    cli,
)

from livekit.plugins import (
    langchain,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
    bey,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel

from graph import create_workflow


from pathlib import Path
load_dotenv(Path(__file__).parent / ".env.local")


class InterviewAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a professional interviewer conducting a job interview. "
                "The LangGraph workflow will drive the conversation flow. "
                "Be conversational, professional, and helpful throughout the interview process."
            )
        )


server = AgentServer()


@server.rtc_session(agent_name="interview-agent")
async def entrypoint(ctx: JobContext):

    # Create the LangGraph workflow
    lg_llm = langchain.LLMAdapter(
        graph=create_workflow()
    )

    # Configure the realtime voice pipeline
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language="multi",
        ),
        llm=lg_llm,
        tts=cartesia.TTS(
            model="sonic-2",
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    # Create the Beyond Presence avatar
    avatar = bey.AvatarSession(
        avatar_id="694c83e2-8895-4a98-bd16-56332ca3f449",
    )

    # Start the avatar
    await avatar.start(
        session,
        room=ctx.room,
    )

    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=InterviewAgent(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    print("Interview agent started.")


if __name__ == "__main__":
    cli.run_app(server)