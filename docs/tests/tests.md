
## So finally we'll perform some tests in 3 modes 
1. vector search only
2. vector search + bm25
3. vector search + bm25 + HyDE

Below list of used queries, reference PDF is RFC2812 - IRC protocol specification.
Used LLM: llama3:8b-instruct-q4_K_M
This folder contains 3 testing result files(chat dumps): 
- vector.json
- vector+bm25.json
- vector+bm25+hyde.json

## Tested
- which command has parameters ( <channel> *( "," <channel> ) [ <key> *( "," <key> ) ] )
- what is the syntax of NICK command
- what replies can JOIN return
- difference between PRIVMSG and NOTICE
- how USER command is structured


| Query N | vector only         | vector + BM25            | vector + BM25 + HyDE |
| ------- | ------------------- | ------------------------ | -------------------- |
| 1       | short, right        | better, more description | very short           |
| 2       | best                | still ok, right          | worse                |
| 3       | fail                | best                     | mid                  |
| 4       | correct, structured | also good                | so short             |
| 5       | fail                | fail                     | OK                   |




## Rest
- what numeric replies are related to WHOIS
- what does QUIT command do
- how to leave a channel
- which command is used to list channels
- what are channel operators
- what errors can happen on KICK
- how INVITE works
- what is TOPIC command format
- what does RFC say about away status