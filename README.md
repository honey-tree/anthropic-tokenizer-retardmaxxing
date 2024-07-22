# Bruteforce Claude 3 Tokenizer (Does not work)

_Not an official implementation_. Originally by _Javier Rando and Florian Tramèr_. If your usage of this tool falls within Anthropic's [Responsible Disclosure Policy](https://www.anthropic.com/responsible-disclosure-policy), we encourage you to follow their protocols.

Forked over javirando's version and attempted to adapt it with the following strategy:

- limit the output tokens to 1
- initiate a prefill string var
- as long as the prefill string does not equal the string being tokenized, keep sending requests with it as the prefill. The content of the new response is the next token, and can be appended to the prefill for the next request.

Anyway the important part is that this does not work. If you try it with a string like

>Good good very berry good.

In the first response, the API will already respond with something mangled like

>content=[TextBlock(text='Goo', type='text')]

And it kind of falls apart from there.

You may be able to force this by sending 
doing something like
```
oldInputTokensCount;

for i := 0; i < len(to_tokenize); i++ {
  message := makeRequest(toTokenize[0:i])
  if message.usage.inputTokenCount > oldInputTokensCount {
    //we have crossed over into a new token, note the old
    //one down somewhere
  }
}
```
but eh, don't see it working either for the same reason.

## Take two

So the next idea was the following:

- set the output tokens back to a big number
- initiate a prefill string var
- set it to a [0:n] substring of the to_tokenize string we're repeating. If Haiku can complete it correctly, then to_tokenize[0:n] is presumably a correct tokenization, and otherwise it isn't (because haiku is stupid, so if the tokenization of the input is incorrect we can expect him to fail to correctly predict the tokens used on the user message). This way, we can progressively tokenize the string.

Anyway this doesn't work either. Not because Haiku succeeds at completing the repetition task when he shouldn't and introduces additional tokens, but because he fails when he should succeed. "ahggihyiuhguh" is one token according to Haiku's text completion skills.

Because Haiku is dumb as bricks. And maybe because Anthropic is ommiting things about how prefills work. One of those, probably.

Also that bit in the code that continues when the new_token ends in a whitespace is there because of the API.
