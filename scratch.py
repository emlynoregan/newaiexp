from openai.embeddings_utils import get_embedding, cosine_similarity
import setcreds

result = get_embedding(["first", "second"], "text-embedding-ada-002")

print(result)

