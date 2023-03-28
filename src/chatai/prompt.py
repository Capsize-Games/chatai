class Prompt:
    def __init__(self, **kwargs):
        self.prefix = kwargs.get("prefix", "")
        self.prompt = kwargs.get("prompt", "")
        self.max_length = kwargs.get("max_length", 512)
        self.min_length = kwargs.get("min_length", 0)
        self.do_sample = kwargs.get("do_sample", False)
        self.early_stopping = kwargs.get("early_stopping", True)
        self.num_beams = kwargs.get("num_beams", 4)
        self.temperature = kwargs.get("temperature", 1.6)
        self.top_k = kwargs.get("top_k", 70)
        self.top_p = kwargs.get("top_p", 1.0)
        self.repetition_penalty = kwargs.get("repetition_penalty", 20.0)
        self.bad_words_ids = kwargs.get("bad_words_ids", None)
        self.length_penalty = kwargs.get("length_penalty", 10.0)
        self.no_repeat_ngram_size = kwargs.get("no_repeat_ngram_size", 1)
        self.num_return_sequences = kwargs.get("num_return_sequences", 1)
        self.use_cache = kwargs.get("use_cache", False)

    def encode(self, tokenizer):
        return tokenizer(self.prompt, return_tensors="pt").input_ids.to("cuda")

    def encode_segments(self, tokenizer):
        # Split the prompt into smaller segments of up to the maximum sequence length
        prefix = ""
        prompt_segments = []
        current_segment = ""
        for word in self.prompt.split():
            if len(current_segment) + len(word) + 1 + len(prefix) <= self.max_length:
                current_segment += " " + word
            else:
                prompt_segments.append(current_segment.strip())
                current_segment = word
        if current_segment:
            prompt_segments.append(current_segment.strip())

        # Encode each segment separately and add the task-specific prefix to the first segment
        encoded_segments = []
        encoded = None
        for i, segment in enumerate(prompt_segments):
            if i == 0:
                encoded = tokenizer.encode_plus(
                    prefix + segment,
                    max_length=self.max_length,
                    truncation=True,
                    padding='max_length',
                    return_tensors='pt'
                )
            else:
                encoded = tokenizer.encode_plus(
                    "<|continuation|>" + segment,
                    max_length=self.max_length,
                    truncation=True,
                    padding='max_length',
                    return_tensors='pt'
                )
            encoded_segments.append(encoded)
        return encoded_segments
