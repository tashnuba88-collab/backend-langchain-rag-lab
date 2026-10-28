# Planning Notes: LangChain RAG API

Complete each section before submitting. Replace every TODO with your own notes.

## 1. System Goal

- User or role: Engineers on the internal platform team who need fast guidance during incidents.
- Business problem: During an incident, engineers need correct, company-specific steps quickly. A general model might invent a process or miss required steps, which can make the incident worse.
- Approved knowledge source: The approved reliability runbooks, stored as chunks in data/runbook_chunks.json and loaded into a Chroma vector store.
- Endpoint route: POST /api/ask

## 2. Manual RAG Workflow Map

Name the manual RAG steps this LangChain version is organizing.

- Receive question: Flask reads the JSON body and validate_question_payload checks and strips the question.
- Retrieve context: retrieve_context searches Chroma for the top_k closest runbook chunks, with distance scores.
- Build prompt: The retrieved chunks are formatted into one context block and filled into the prompt template along with the question.
- Call model: The chain sends the filled prompt to the local Ollama chat model (llama3.2).
- Parse or format output: StrOutputParser turns the model reply into a plain string, and the response formatter wraps it in the API response shape.
- Return sources: format_sources returns source metadata (id, title, category, section, chunk id, distance) without the full document text.
- Verify quality: Empty model output is rejected, and the pytest suite checks validation, formatting, retrieval, service flow, and route behavior.

## 3. LangChain Component Mapping

Map the manual workflow to LangChain-supported pieces.

- Prompt string maps to: ChatPromptTemplate, with {context} and {question} placeholders.
- Chroma search logic maps to: The Chroma vector store from langchain_chroma, queried with similarity_search_with_score.
- Direct model call maps to: ChatOllama from langchain_ollama.
- Function-to-function workflow maps to: A chain built with the pipe operator: prompt_template | llm | StrOutputParser().
- Manual output cleanup maps to: StrOutputParser.
- Manual testing maps to: Automated pytest tests that use fake vector stores and fake chains, so no live Ollama or Chroma data is needed.

## 4. Response Contract

List the fields a successful response should include.

- answer: The grounded answer text from the model.
- sources: A list of source metadata objects (source_id, title, category, section, chunk_id, distance) with no full document text.
- langchain: Debug metadata showing the chain expression, components, retrieved count and chunk ids, top_k, context length, fallback status, and score type.

## 5. Fallback Behavior

Explain what the system should do when no approved context is available.

If retrieval returns no documents, or only documents with blank text, the service does not call the model. It returns a fixed safe answer saying there is not enough approved runbook context to answer reliably, an empty sources list, and langchain.fallback set to true. This stops the model from guessing or inventing incident steps when the runbooks have nothing relevant.

## 6. Verification Plan

List at least four checks you should run before trusting the refactor.

- Run the full pytest suite and confirm every test passes.
- Ask an in-scope question (for example, about checkout API errors after a release) and confirm the answer matches the runbook and the sources list the right chunks.
- Ask an out-of-scope question (for example, about office lunch policy) and confirm the fallback response comes back with empty sources and fallback set to true.
- Send bad requests (empty body, missing question, non-string question, very short and very long questions) and confirm each returns HTTP 400 with the right error code.
- Confirm sources contain only metadata and distance, with no full document text.
- Confirm app.py contains no prompt, retrieval, or model code, so the route stays a thin layer over the service.

## 7. Reflection

Explain what LangChain simplified and what may be harder to inspect.

LangChain simplified how the workflow is organized. The prompt, model, and parser connect in one readable chain, and the Chroma and Ollama wrappers replaced code I would have written by hand. Swapping the model or the document collection would mean changing a small amount of code. What got harder to inspect is what happens inside the chain, since the filled prompt and raw model output are not visible unless I log them. Retrieval quality also still needs my own checking, because LangChain does not tell me whether the chunks it returned were actually relevant. That is why I kept the debug metadata in the response and the fallback check in the service.
