from .models import Cuisine, Restaurant
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel


# Load pre-trained CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Predefined cuisines or food categories
def get_cuisines():
  unique_cuisines = Cuisine.objects.values_list('name', flat=True).distinct()
  print(list(unique_cuisines))
  return list(unique_cuisines)

def batch_texts(texts, batch_size):
    for i in range(0, len(texts), batch_size):
        yield texts[i:i + batch_size]

# Load and preprocess the image
def classify_cuisine(image_path):

    image = Image.open(image_path).convert("RGB")

    # Process inputs for CLIP
    cuisine_texts = get_cuisines()

    predicted_cuisine_per_batch = []
    for batch in batch_texts(cuisine_texts, batch_size=15):
      inputs = processor(text=batch, images=image, return_tensors="pt", padding=True)
      outputs = model(**inputs)
      logits_per_image = outputs.logits_per_image
      probs = logits_per_image.softmax(dim=1)
      max_prob, best_idx = probs.max(dim=1)
      print(batch[best_idx.item()])
      predicted_cuisine_per_batch.append(batch[best_idx.item()])
    
    print(predicted_cuisine_per_batch)
    final_inputs = processor(text=predicted_cuisine_per_batch, images=image, return_tensors="pt", padding=True)
    final_outputs = model(**final_inputs)
    logits_per_image = final_outputs.logits_per_image
    final_probs = logits_per_image.softmax(dim=1)
    max_prob, best_idx = final_probs.max(dim=1)
    print(max_prob.item())
    print(predicted_cuisine_per_batch[best_idx.item()])

    return predicted_cuisine_per_batch[best_idx.item()]

