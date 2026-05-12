from google import genai


DEFAULT_PROMPT_TEMPLATE = """\
You are a query expansion assistant for a semantic search engine over technical \
infrastructure documentation. Your job is to rewrite the user query into a \
richer version that includes synonyms, related technical concepts, and \
alternative phrasings that would help retrieve relevant document chunks.

Return ONLY the expanded query as a single paragraph. No explanations, no bullet \
points, no preamble.

Original query: {query}

Expanded query:
"""


class GeminiModelAdapter:
    """
    Adapter around Gemini SDK so the rest of the codebase
    can stay model-agnostic.
    """

    def __init__(self, client, model_name="gemini-2.5-flash"):
        self.client = client
        self.model_name = model_name

    def generate_content(self, prompt: str):
        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )


class QueryExpander:
    """
    Wraps any model object that exposes:
        .generate_content(prompt)
    """

    def __init__(
        self,
        model,
        expansion_prompt_template: str = DEFAULT_PROMPT_TEMPLATE
    ):
        self._model = model
        self._prompt_template = expansion_prompt_template

    def expand(self, query: str) -> str:
        prompt = self._prompt_template.format(query=query)

        response = self._model.generate_content(prompt)

        return response.text.strip()

    def expand_batch(self, queries: list[str]) -> list[str]:
        return [self.expand(q) for q in queries]


def create_gemini_expander(api_key: str) -> QueryExpander:
    """
    Factory — creates a Gemini-backed QueryExpander.
    """

    client = genai.Client(api_key=api_key)

    model_adapter = GeminiModelAdapter(client)

    return QueryExpander(model=model_adapter)

