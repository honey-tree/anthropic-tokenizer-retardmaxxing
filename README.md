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
but eh, don't see it working either.

