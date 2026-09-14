# AI Voice Interview Agent

A real-time, voice-driven AI interviewer built on **LiveKit Agents**, **LangGraph**, and **Retrieval-Augmented Generation (RAG)**. Candidates have a natural spoken conversation with an AI interviewer — complete with a synced virtual avatar — that asks structured interview questions, listens and responds in real time, and can answer candidate questions about the company by grounding its answers in an internal company document.

## Features

- **Real-time voice conversation** over WebRTC via the LiveKit Agents framework
- **Structured interview flow** orchestrated with LangGraph — introduction → technical background → behavioral/challenge question → open candidate Q&A
- **Retrieval-Augmented Generation (RAG)** pipeline (LangChain + OpenAI embeddings + ChromaDB) that grounds company-related answers in an ingested company PDF instead of hallucinating
- **Autonomous tool use** — the LLM decides when to call:
  - `company_info_tool` to retrieve relevant company info
  - `record_answer_tool` to log the candidate's response
- **Full speech pipeline**: Deepgram (speech-to-text) → GPT-4o reasoning via LangGraph → Cartesia (text-to-speech), with Silero VAD and multilingual turn detection for natural back-and-forth timing
- **Background noise cancellation** (LiveKit BVC)
- **Animated virtual avatar** via Beyond Presence, lip-synced to the agent's speech in real time

## How It Works

1. A candidate joins a LiveKit room; the agent is dispatched and joins alongside a Beyond Presence avatar participant.
2. Speech is transcribed live by Deepgram and streamed into a **LangGraph** state machine.
3. The graph's LLM node (GPT-4o) decides whether to respond directly, call `company_info_tool` (RAG lookup against the company PDF via ChromaDB), or call `record_answer_tool` to log the candidate's answer.
4. Responses are streamed to Cartesia for text-to-speech, played back through the room, and mirrored by the avatar.
5. The graph loops between the LLM node and its tool-executor node until the interview's four stages are complete.

## Project Structure

```
livekit-voice-agent/
├── agent.py              # LiveKit entrypoint — voice pipeline, avatar, session wiring
├── graph.py               # LangGraph workflow — RAG tools, interview state machine
├── pyproject.toml         # Project metadata & dependencies (uv)
├── uv.lock                # Locked dependency versions
├── livekit.toml            # LiveKit CLI/project config
├── Dockerfile               # Container build for deployment
├── .dockerignore
├── .env.local               # Local secrets (never committed — see below)
├── chroma_store/             # Persisted vector DB (generated at runtime)
├── interview_answers.txt      # Logged candidate answers (generated at runtime)
└── README.md
```

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependency management
- A [LiveKit Cloud](https://cloud.livekit.io) project
- API keys for OpenAI, Deepgram, Cartesia, and Beyond Presence

## Setup

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Configure environment variables** — create `.env.local` in the project root:

   | Variable | Description |
   |---|---|
   | `LIVEKIT_URL` | Your LiveKit Cloud project URL, e.g. `wss://your-project.livekit.cloud` |
   | `LIVEKIT_API_KEY` | From your LiveKit Cloud project settings |
   | `LIVEKIT_API_SECRET` | From your LiveKit Cloud project settings |
   | `OPENAI_API_KEY` | For GPT-4o and text-embedding-3-small |
   | `DEEPGRAM_API_KEY` | For speech-to-text |
   | `CARTESIA_API_KEY` | For text-to-speech |
   | `COMPANY_PDF_PATH` | *(optional)* Path to the company info PDF used for RAG |
   | `CHROMA_DIR` | *(optional)* Vector store directory, defaults to `./chroma_store` |

   > Check the `livekit-plugins-bey` docs for whether it needs its own API key variable (e.g. `BEY_API_KEY`) in addition to the avatar ID configured in `agent.py`.

3. **Add your company document** — place a PDF at the path set in `COMPANY_PDF_PATH` (or the default in `graph.py`). This is what the RAG pipeline retrieves from when candidates ask company questions.

4. **Run the agent**
   ```bash
   uv run agent.py dev
   ```

5. **Test it** — in your LiveKit Cloud project, go to **Agents → Console** and click **Start a session** to talk to the agent live with transcripts, events, and metrics.

## Known Limitations / Future Improvements

- Uses **explicit dispatch** (`agent_name="interview-agent"`), so it won't auto-join arbitrary rooms — intentional for controlled interview sessions, but worth knowing if extending this.
- Supports a single company PDF at a time; no multi-tenant/multi-company support yet.
- Candidate answers are logged in plaintext to `interview_answers.txt` — fine for a personal/demo project, but would need proper storage and consent handling before any real candidate data touches it.
- No persistent session/resume support if a candidate disconnects mid-interview.
- Potential roadmap: a simple web front-end for candidates, a reviewer dashboard for transcripts, and configurable question sets per role.

## License

Released under the [MIT License](LICENSE). Note that running this project still requires your own paid API keys for LiveKit, OpenAI, Deepgram, Cartesia, and Beyond Presence — the license covers the code, not access to those services.
