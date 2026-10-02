# Claude Certified Developer – Foundations (CCDV-F)
## The Actual Content — Read This, Memorize This

This is the study material itself, not a schedule. Each day below covers its domains with real definitions, explanations, comparisons, and examples. Read top to bottom; nothing here is a placeholder for outside reading.

Quick exam facts, since you'll want them once: 53 questions, 120 minutes, Pearson VUE, pass at 720/1000, $125, 12-month validity, closed-book.

---

# DAY 1 — Applications & Integration, Part 1

## 1.1 The Messages API — the actual shape of a request

Every call to Claude looks like this:

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "system": "You are a helpful assistant that only answers in JSON.",
  "messages": [
    {"role": "user", "content": "What's the capital of France?"}
  ]
}
```

**Memorize these facts:**
- `system` is a **top-level parameter**, not a message in the `messages` array. It sets persistent behavior for the whole conversation and is the highest-priority instruction layer.
- `messages` alternates `user` and `assistant` roles. You cannot send two `user` messages in a row without an `assistant` message between them (in a single API call's message list) — the API will reject malformed alternation in most SDKs, though some flexibility exists for multi-content-block turns.
- `content` can be a plain string OR an array of **content blocks** — this matters because tool calls, images, and thinking output are all delivered as distinct block types (`text`, `image`, `tool_use`, `tool_result`, `thinking`) inside that array, not as separate API fields.
- `max_tokens` is required and caps the *output* length — it does not cap the input.

**Why this is tested:** questions will present a malformed request (system prompt inside `messages`, wrong role order, missing `max_tokens`) and ask you to spot the mechanical error.

## 1.2 stop_reason — the single most testable API mechanic

Every response includes a `stop_reason` field. Memorize all four values:

| `stop_reason` | Meaning | What you do next |
|---|---|---|
| `end_turn` | Model finished naturally | Nothing — this is a complete answer |
| `max_tokens` | Hit the `max_tokens` cap mid-generation | Response is truncated; increase the limit or handle partial output |
| `tool_use` | Model wants to call a tool | Execute the tool, return a `tool_result` block, send it back |
| `stop_sequence` | Hit a custom stop string you defined | Response ended at your defined boundary |

**Why this is tested:** a scenario will describe an agent loop that never terminates, or output that's silently cut off, and the fix is always "check `stop_reason` — you're not handling `max_tokens` (truncation) or you're not looping on `tool_use` correctly."

## 1.3 Tool use — the full mechanics

A tool is defined with a name, description, and JSON Schema input:

```json
{
  "name": "get_weather",
  "description": "Get current weather for a city. Use this whenever the user asks about weather, temperature, or conditions in a specific location.",
  "input_schema": {
    "type": "object",
    "properties": {"city": {"type": "string"}},
    "required": ["city"]
  }
}
```

**`tool_choice` has four settings — memorize all four:**
- `auto` (default) — model decides whether to call a tool or answer directly
- `any` — model must call *some* tool, but can pick which one
- `tool` (with a specific name) — model is forced to call that exact tool
- `none` — model is blocked from calling any tool, even if one is available

**The loop**, step by step:
1. You send a message + tool definitions.
2. Model responds with `stop_reason: tool_use` and a `tool_use` content block containing the tool name + input.
3. Your code executes the actual function.
4. You send a new message with role `user`, containing a `tool_result` content block that references the original `tool_use_id` and holds the function's output.
5. Model reads the result and either calls another tool or produces `end_turn`.

**Tool description quality is directly tested.** A vague description ("gets data") causes the model to misuse or skip the tool. A good description states *when* to use it, not just *what* it does — that's the exact distinction the exam rewards.

## 1.4 Streaming

Streaming delivers the response as a sequence of Server-Sent Events instead of one blocked response. Event types you should recognize by name: `message_start`, `content_block_start`, `content_block_delta` (the actual incremental text/tokens), `content_block_stop`, `message_delta`, `message_stop`.

**Use streaming when:** the response is user-facing and perceived latency matters (a chat UI). **Don't bother streaming when:** you need the full response before doing anything with it anyway (e.g., feeding it straight into another function call) — streaming adds complexity with no benefit there.

## 1.5 Vision

Images are sent as a content block with `type: "image"` and a `source` object (`type: "base64"`, `media_type`, `data`). Multiple images can appear in one message; the model reads them in the order they're given, and you should reference them by position or label in your text prompt ("the first image shows... the second shows...") because the model doesn't have inherent image identifiers.

## 1.6 Extended / adaptive thinking

When enabled, the model returns a `thinking` content block *before* its final answer — this is the model's internal reasoning, returned as a distinct block, not mixed into the final text. **Adaptive thinking** means the model adjusts how much reasoning it does based on task difficulty rather than using a fixed budget every time. **Effort levels** are a way to explicitly control how much computation/reasoning the model applies — higher effort = more thorough reasoning, higher latency and cost.

## 1.7 Prompt caching — the concept, the mechanics, the economics

**Concept:** if you send the same large block of content (a long system prompt, a big set of few-shot examples, a large document) repeatedly across calls, you can mark it as a **cache breakpoint** so Claude doesn't have to reprocess it from scratch every time.

**Mechanics:** you insert a `cache_control` marker on a content block. On the first call, that block is written to cache (costs slightly more than normal input). On subsequent calls within the cache lifetime, a **cache hit** reads that block at a steep discount instead of paying full input price.

**When it pays off — memorize this trigger condition:** large, stable content reused across many calls. It does NOT pay off for content that changes on every call (e.g., unique user questions) — there's nothing to cache there.

## 1.8 Message Batches API — memorize the exact trigger phrase

**Batches API** = submit many requests asynchronously, get results later (not immediately), at a lower cost than realtime calls.

**The exact condition the exam rewards:** "high-volume" + "latency-tolerant." If a scenario says "process 10,000 documents overnight" or "no user is waiting on this," the answer is Batches. If a scenario says "user is waiting in a chat window," the answer is realtime/streaming.

## 1.9 Third-party vendor access

Claude is also available through **Amazon Bedrock** and **Google Cloud Vertex AI**, in addition to Anthropic's direct API. You need to recognize these names as valid deployment paths, not deep configuration knowledge of either.

## 1.10 Software Engineering Foundations

- **REST**: stateless HTTP calls, resources identified by URLs, standard verbs (GET/POST/PUT/DELETE). Claude's API is REST-based — every SDK (Python, TypeScript, etc.) is a thin wrapper around REST calls, not a separate protocol.
- **Asynchronous programming**: don't block a thread waiting on a Claude API call in a server handling multiple requests — use `async`/`await` (Python/TypeScript) so other requests can be processed while one is waiting on the network.
- **Version control**: meaningful, atomic commits; feature branches; the exam expects you to recognize good vs. bad git hygiene as a general engineering competency, not Claude-specific.
- **Code review & refactoring**: same — general software judgment, applied to AI-integrated codebases (e.g., recognizing that a prompt embedded as a giant inline string with no version control is a refactoring smell).

## 1.11 Requirements & Systems Life Cycle

Standard SDLC phases: **requirements → design → build → test → deploy → maintain.** The Claude-specific wrinkle tested here: requirements for an LLM feature must define **success criteria for non-deterministic output** (e.g., "the summary must contain the key figures" rather than "the summary must exactly match this text") — because you cannot spec exact output the way you would for deterministic software.

---

# DAY 2 — Applications & Integration, Part 2 + Model Selection and Optimization

## 2.1 Claude across surfaces — know the differences

| Surface | What's distinct about it |
|---|---|
| **claude.ai** | Consumer chat interface; artifacts, projects, memory features |
| **Claude Desktop** | Local app; can connect to MCP servers running on your machine |
| **Claude Code** | CLI/agentic coding tool; reads `CLAUDE.md`, has file system + shell access |
| **The API** | Raw programmatic access; you control everything — system prompt, tools, context |
| **SDKs (Agent SDK, client SDKs)** | Higher-level wrappers; the Agent SDK specifically manages the agent loop for you |

**Why tested:** a question may describe unexpected model behavior and the fix is recognizing that the surface itself has different default context or tool access than the one the question-writer assumed — e.g., Claude Code has file access that the raw API does not have by default.

## 2.2 Content boundaries

Some behaviors are not unlockable by system prompt or user instruction, regardless of how the request is framed. The exam wants you to recognize that "just tell it to ignore its guidelines" is never a valid engineering solution to unwanted refusals — the correct response in an application is to redesign the request or handle the refusal gracefully in code, not to try to override behavior via prompting.

## 2.3 Schema design for tools

A well-designed tool input schema:
- Uses precise types (`string`, `integer`, `boolean`, `enum` where applicable) rather than accepting free-text for structured values
- Marks fields `required` only when truly required
- Uses `enum` to constrain a field to a fixed set of valid values instead of hoping the model guesses correctly

Bad schema design (accepting a free-text "action" field instead of an enum of valid actions) is a common exam distractor — the "wrong" answer usually looks convenient but produces unreliable parsing downstream.

## 2.4 Session hygiene

Long-running conversations accumulate irrelevant history. **Session hygiene** = actively managing what stays in context: trimming old turns that no longer matter, starting a fresh session when the task changes, and not letting a single session run indefinitely just because the API technically allows it. This connects directly to Day 4's context engineering material.

## 2.5 Plugin management

Plugins package reusable functionality (tools, skills, configuration) that can be enabled per project or per user. The exam-relevant point: plugins have **dependencies** that must be tracked and versioned like any other software dependency — an untracked plugin update can silently change application behavior.

## 2.6 Configuration Management

- **`CLAUDE.md`**: a file (or hierarchy of files — project-level, user-level) that gives Claude Code standing instructions about the codebase, conventions, and constraints. It's read automatically at session start.
- **`settings.json`**: configuration for Claude Code behavior — permissions, tool access, model selection at the config level.
- **Model version pinning**: in production, you specify an exact model string (e.g., `claude-sonnet-4-6`) rather than an alias like "latest." **Why this is tested constantly:** Anthropic can and does make breaking behavior changes across model versions — an application pinned to "latest" can silently change behavior overnight with zero code changes on your end. The correct practice is always: pin the exact version, test new versions in staging before switching, then update the pin deliberately.
- **Prompt versioning**: treat prompts like code — track changes, test changes, don't edit production prompts in place without review.

## 2.7 Model Selection — the tradeoff triangle (memorize this cold)

| Model tier | Best for | Cost | Latency | Reasoning depth |
|---|---|---|---|---|
| **Haiku** | High-volume, simple, latency-sensitive tasks (classification, extraction, simple chat) | Lowest | Fastest | Lowest |
| **Sonnet** | The balanced default for most production applications | Medium | Medium | Medium-high |
| **Opus** | Highest-complexity reasoning, where quality matters more than cost or speed | Highest | Slowest | Highest |

**The exact exam pattern:** a scenario describes constraints (e.g., "millions of simple classification calls per day, cost is the primary concern" → Haiku; "complex multi-step legal analysis, occasional use, accuracy is critical" → Opus; "general customer support chatbot, moderate volume" → Sonnet). You are not expected to know exact pricing numbers — you're expected to correctly map constraint → tier.

**Breaking changes across releases:** never assume a new model version behaves identically to the old one on your exact prompts. Re-test before switching production traffic.

## 2.8 LLM Fundamentals — the concepts behind the API

- **Tokens**: the unit the model processes text in — not exactly words, not exactly characters. Both input and output are measured and billed in tokens.
- **Context window**: the total tokens (input + output combined, within a single call) the model can handle at once. Exceeding it means truncation or an error, depending on implementation.
- **Sampling / non-determinism**: even at the same input, output can vary between calls because generation involves probabilistic sampling over possible next tokens. **This is directly testable**: if a scenario needs perfectly reproducible output every time, you cannot guarantee that from the model alone — you need deterministic post-processing/validation around it, not a prompting trick.
- **Fast mode**: a mode/setting oriented toward lower latency at some cost to depth of processing — appropriate when speed matters more than maximum quality.
- **Effort levels**: explicit control over how much computation the model applies to a task.
- **Zero-shot → multi-shot spectrum**: zero-shot = no examples given; few-shot/multi-shot = you provide example input/output pairs in the prompt to steer format and behavior. More examples generally improve consistency of output format at the cost of more input tokens (and thus more cost, and more relevance to prompt caching from Day 1).

## 2.9 Cost and Token Management

- **Usage tracking**: monitoring token consumption per request/user/feature to understand where cost is concentrated.
- **Cost modeling**: estimating total cost = (input tokens × input price) + (output tokens × output price), summed across expected call volume, per model tier.
- **Cache checkpointing**: deliberately structuring your prompt so the large, stable portion (system prompt, few-shot examples) is cached, and only the small, variable portion (the user's actual new question) is processed fresh each time — this is the concrete technique that makes Day 1's prompt caching concept pay off financially at scale.

---

# DAY 3 — Agents and Workflows + Tools and MCPs

## 3.1 Workflow vs. Agent — the single most important distinction in this domain

**Workflow**: a fixed, predetermined sequence of steps you define in code. The LLM might be called at one or more steps, but the *order and structure* of steps is decided by your code, not by the model.

**Agent**: the model itself decides, at runtime, what steps to take next, in what order, using its own judgment — typically via a loop where it repeatedly chooses to call tools or respond, based on what it observes at each step.

**Decision rule — memorize this exactly:** if the task is predictable and repeatable (the same steps every time, just with different data), use a **workflow** — it's cheaper, faster, and more reliable. If the task requires judgment about what to do next that can't be hard-coded in advance (the right next step depends on what happened in the previous step, in ways you can't fully anticipate), use an **agent**.

## 3.2 Manager/supervisor hierarchies and subagents

A **manager/supervisor** pattern has one top-level agent that delegates subtasks to other agents rather than doing everything itself. A **subagent** is a delegated agent handling a bounded piece of the overall task, typically with its **own separate context window** — this is deliberate: it keeps the manager's context clean and keeps the subagent focused only on what it needs for its specific job.

## 3.3 Agent construction — the Claude Agent SDK and custom loops

The **Claude Agent SDK** is Anthropic's higher-level SDK that handles the agent loop (call model → check for tool use → execute tool → feed result back → repeat) for you, so you don't hand-write that loop yourself.

A **custom agent loop/harness** is what you build when you implement that same loop manually using the raw Messages API — more control, more code to maintain.

**Self-hosted vs. Anthropic-hosted managed agents**: self-hosted means you run the agent infrastructure yourself (your servers, your orchestration code); Anthropic-hosted managed agents means the execution environment is provided/managed by Anthropic. Know this distinction exists as a deployment choice with different operational responsibility.

**Hooks**: deterministic code that runs at fixed points in the agent loop — e.g., "before every tool call, check permissions" or "after every tool call, log the result." Hooks exist specifically because you can't fully trust the model to self-enforce a rule 100% of the time; a hook enforces it in code, guaranteed, every single time. This concept reappears in Day 4 as a security mechanism.

## 3.4 Agent patterns and frameworks

- **Tool-use loop**: the fundamental repeating cycle (model call → tool call → result → model call...) underlying every agent.
- **Memory**: how an agent retains information across turns or sessions beyond just the raw conversation history (e.g., a structured summary or external store).
- **Context-window management in long agent runs**: as an agent takes many steps, its context fills with tool outputs and history — without active management this leads to the "drift and bloat" problem covered fully in Day 4.
- **Frameworks to recognize by name** (not deep expertise needed): **Strands, LangGraph, PydanticAI** — third-party abstraction layers for building agents/workflows. Know they exist as alternatives to hand-rolling everything or using the Agent SDK directly.

## 3.5 Tool Implementation

- **Function calling**: the general mechanism (covered mechanically in Day 1, section 1.3) — the model requests a function call, your code executes it.
- **Tool description writing**: reiterating from Day 1 because it's tested from two angles (mechanics AND design quality) — a good description tells the model *when* to use the tool, with enough specificity to disambiguate it from similar tools.
- **Error handling inside tool execution**: if a tool call fails (bad input, downstream API error), you should return a `tool_result` that clearly communicates the failure back to the model — so it can retry, ask for clarification, or fall back — rather than letting your code crash or silently returning empty/wrong data.
- **Client-side vs. server-side tools**: client-side tools execute in the calling application's own environment (you write and run the function); server-side tools are executed by Anthropic's infrastructure itself (e.g., a hosted web search or code execution tool) without you implementing the execution logic.
- **Approval patterns**: gating risky tool calls (e.g., anything that sends money, deletes data, or sends external communications) behind a human confirmation step before execution — a human-in-the-loop control, not a fully autonomous one.

## 3.6 MCP Server Development

**MCP (Model Context Protocol)** standardizes how an LLM application exposes and consumes **tools, resources, and prompts** — so a tool built once as an MCP server can be reused by *any* MCP-compatible client (Claude Desktop, Claude Code, a custom app), not just one specific application's codebase.

An MCP server exposes three kinds of primitives: **tools** (callable functions), **resources** (readable data/content the client can pull in), and **prompts** (reusable prompt templates the server provides).

**Transports**: **stdio** (the server runs as a local subprocess, communicating over standard input/output — typical for local/desktop use) vs. **socket/HTTP-based transport** (the server runs remotely/as a service, communicating over a network connection — typical for shared, multi-client, or remote deployments).

## 3.7 Agentic Customization — the full tradeoff matrix (memorize this table)

| Option | Best when | Tradeoff |
|---|---|---|
| **Built-in tool** | The exact capability already exists as a hosted tool (e.g., web search) | Fastest to use, zero build effort, but you can't customize its internals |
| **Custom tool** | You need a specific function tightly scoped to one application | Full control, but only reusable within that one application's code |
| **Skill** | You need a reusable *instruction package* (not necessarily code) that Claude can invoke | Reusable across sessions/projects using that skill system, but it's instructions, not a general-purpose remote service |
| **MCP server** | The same tool/resource needs to be reused **across multiple different applications or clients** | Most reusable, but has the most setup/deployment overhead |

**The exact trigger phrase to memorize:** MCP is the right choice specifically when reuse needs to span **multiple separate applications/clients** — not just multiple calls within one app (that's just a well-designed custom tool).

---

# DAY 4 — Prompt & Context Engineering, Security, Claude Code, Eval/Debugging

## 4.1 Context Engineering — this is your newer material, read carefully

**Context-window management**: actively deciding what stays in the model's input at each turn, rather than just letting history accumulate unchecked.

**Drift**: the model's behavior gradually deviating from original instructions as a long conversation accumulates tangential content that dilutes or contradicts the original system prompt's intent.

**Bloat**: the context window filling with content that isn't actually useful anymore (old tool outputs, resolved sub-tasks, repeated information) — this costs tokens/money and can actively hurt output quality, not just efficiency.

**Tool-output pruning**: when a tool returns a large result (e.g., a full API response, a long document), you don't have to keep the entire raw output in context forever — trim it down to just the relevant parts before it re-enters the conversation on subsequent turns.

**Compaction**: instead of either (a) keeping all raw history forever, or (b) deleting old history outright, you **summarize** older context into a condensed form that preserves the important information while freeing up token budget.

**Context isolation through subagents**: giving a subagent (from Day 3) its own separate, clean context window so that its intermediate work (many tool calls, lots of exploration) doesn't pollute the main agent's context — only the subagent's *final result* gets passed back up.

## 4.2 Prompt Engineering — fast refresher (you already know this)

- **Instruction clarity**: explicit, unambiguous instructions outperform vague ones.
- **Few-shot examples**: providing example input/output pairs to steer format/behavior; effective but costs input tokens (ties to caching).
- **System vs. user placement**: stable, persistent behavior rules go in `system`; per-turn, variable content goes in `user` messages.
- **Output constraints**: explicitly specifying the required output format (e.g., "respond only in valid JSON matching this schema") reduces parsing failures downstream.
- **Iterative refinement**: testing and adjusting a prompt against real examples rather than assuming it's correct on the first attempt.
- **Input sanitization**: treating any text that originated from a user or an external source as **data to be evaluated**, not as instructions to be obeyed — this is the direct link to prompt injection defense in section 4.4.

## 4.3 Output Handling

- **Structured output patterns**: constraining the model to produce output in a fixed, parseable shape (JSON, a specific schema) so your application code can reliably consume it without fragile string-parsing.
- **Response validation**: after receiving structured output, actually validate it against the expected schema in code before using it — don't assume the model's output is always well-formed just because you asked for a format.
- **Defensive parsing**: write parsing code that handles the case where the model's output is malformed, incomplete, or unexpected — catch and handle it, don't let it crash your application.
- **Skepticism toward confident output**: the model can produce fluent, confident-sounding output that is factually wrong or logically inconsistent — application design should include verification steps for anything high-stakes, rather than trusting output purely because it "sounds right."

## 4.4 AI Application Security — memorize the combined-defense pattern

**Prompt injection**: malicious instructions embedded in content the model processes (a document, a webpage, a tool result, user input) that attempt to override the system prompt's original instructions.

**Jailbreak defense**: techniques and design choices that resist attempts to get the model to bypass its guidelines through clever prompting.

**Untrusted input handling**: any content not directly authored by your trusted system prompt — user messages, retrieved documents, tool outputs, third-party API responses — should be treated as potentially adversarial data.

**Data leakage prevention**: ensuring sensitive information (secrets, other users' data, internal system details) doesn't get exposed in model output, especially when the model has broad context access.

**PII handling**: personally identifiable information needs specific handling — minimization, redaction, or restricted access — separate from general data leakage concerns.

**The memorized correct-answer pattern for injection questions:** the right answer combines **isolating/sanitizing untrusted content** *plus* **least-privilege guardrails** on what the model/agent is allowed to do — never just one alone. A model that reads a poisoned document but has no ability to take a harmful action (because of least privilege) is much safer than relying on the model to "recognize" the injection and refuse it.

## 4.5 Guardrails and Safe Deployment

- **Content policy**: rules about what content is or isn't acceptable output for your specific application, layered on top of the model's own built-in behavior.
- **Guardrail layering**: never rely on a single check — combine multiple independent safeguards (input validation, output filtering, permission scoping) so one failure doesn't compromise the whole system.
- **Least privilege**: a tool, agent, or integration should have the minimum access/permissions necessary to do its job — nothing more. This is the single most repeated security principle across this whole domain.
- **Identity and access management (IAM)**: standard access-control practices — authenticating who/what is making a request, and authorizing only what they're permitted to do.

## 4.6 Claude Hooks for Guardrails

Reiterating from Day 3 with the security framing: a **hook** is deterministic code that runs at a fixed point (e.g., before a tool executes) and can **block** an action outright — this guarantees enforcement in a way that relying on the model's own judgment cannot, because hooks run every time, with no exceptions, regardless of what the model "decides."

## 4.7 Identity, Secrets, and Key Management

- Never hardcode API keys in source code or prompts.
- Use environment variables or a secrets manager, and scope different keys to different environments (dev/staging/production) so a leaked dev key can't touch production.
- Rotate credentials periodically and immediately after any suspected exposure.

## 4.8 Claude Code — the core vocabulary (cap your time here, this domain is 3.1%)

- **Rules**: standing behavioral instructions for a Claude Code session/project.
- **Skills**: reusable instruction packages Claude Code can invoke for specific task types.
- **Commands**: slash commands — shortcuts that trigger predefined actions/prompts.
- **Agents**: sub-configurations within Claude Code for specific delegated roles.
- **Agent Memory**: persistent information retained across sessions, not just within one conversation.
- **`CLAUDE.md` hierarchy**: multiple levels (e.g., project-level and user-level) that combine to form the full standing instructions for a session — project-level typically takes precedence for project-specific conventions.
- **`settings.json`**: configuration file controlling permissions and behavior.
- **Headless mode**: running Claude Code non-interactively (e.g., inside a CI/CD pipeline) without a live terminal session driving it turn by turn.
- **Streaming mode**: output delivered incrementally rather than all at once, same underlying concept as Day 1's API streaming, applied within Claude Code's interface.

## 4.9 Eval, Testing, and Debugging (2.6% — smallest domain, don't over-invest)

**The core diagnostic skill, in order:**
1. **Is this an application-layer bug or a model-output problem?** Always ask this first. If your code mishandles a correctly-formed response (e.g., broken JSON parsing logic), that's an application bug. If the model itself produced wrong or malformed content despite correct application code, that's a model-output problem.
2. **Error type identification**: classify the failure — malformed input to the API, a tool execution error, a parsing failure, or genuinely incorrect model reasoning — these require different fixes.
3. **Trace analysis**: read the full request/response trace (including intermediate tool calls in an agent loop) to find exactly where the pipeline diverged from expected behavior, rather than guessing from the final output alone.
4. **Recovery strategies**: once you know the failure type, the standard toolkit is — retry (for transient errors), fall back to a different model or simpler approach (for capability mismatches), or escalate to a human (for cases requiring judgment your system can't provide).

---

# DAY 5 — This is Practice Day, Not New Content

Day 5 in the schedule is entirely mock exam + weak-spot re-reading from the four days above. There's no new material to add here — go back to this document and re-read only the sections that correspond to whatever your practice questions revealed as weak.

---

# Final Memorization Sheet — the 10 facts most likely to directly decide a question

1. `stop_reason` values: `end_turn`, `max_tokens`, `tool_use`, `stop_sequence`.
2. `tool_choice` values: `auto`, `any`, `tool`, `none`.
3. Batches API = high-volume + latency-tolerant. Realtime/streaming = interactive/user-facing.
4. Workflow = fixed steps you define. Agent = model decides its own steps at runtime.
5. MCP's specific advantage over a custom tool: reuse across **multiple separate applications/clients**.
6. Model tiers: Haiku = cheap/fast/simple. Sonnet = balanced default. Opus = highest reasoning need.
7. Prompt injection defense = isolate/sanitize untrusted input **AND** least-privilege guardrails, always both.
8. Never pin to "latest" in production — pin an exact model version; breaking changes happen across releases.
9. Prompt caching pays off on large, stable, reused content — not on unique per-call content.
10. First debugging question, always: application-layer bug, or model-output problem?

---

*Sourcing note: content is built from the published CCDV-F exam blueprint (domains and sub-skill weights) cross-referenced across multiple independent secondary sources, combined with standard, well-established Claude API/Agent SDK/MCP/Claude Code mechanics. This is a new certification (opened July 2026) with no official practice exam published, so treat this as a high-confidence study document rather than a verified match to exact exam wording.*

