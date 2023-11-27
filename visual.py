import gradio as gr
from Greibach import *


def visual(Input, operation, sentence):
    
    if operation == "消除无用符号":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        print(G)
        return G, G.isInNF(G)

    if operation == "消除左递归":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        print(G)
        return G, G.isInNF(G)
    
    if operation == "消除空产生式":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        print(G)
        return G, G.isInNF(G)
    
    if operation == "消除单一产生式":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        G._removeUnitProductins()
        print(G)
        return G, G.isInNF(G)
    
    if operation == "生成Greibach范式":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        G._removeUnitProductins()
        G._terminateFirstSymbol()
        G._renameCFG()
        print(G)
        return G, G.isInNF(G)
    
    if operation == "Greibach范式验证":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        G._removeUnitProductins()
        G._terminateFirstSymbol()
        G._renameCFG()
        print(G)
        return G, G.isInNF(G)
    
    if operation == "PDA规则生成":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        G._removeUnitProductins()
        G._terminateFirstSymbol()
        G._renameCFG()
        npda, PDA = G.pda()
        print(G.printPDA(PDA))
        return G.printPDA(PDA), None
    
    if operation == "PDA单步运行":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        G._removeUnitProductins()
        G._terminateFirstSymbol()
        G._renameCFG()
        npda, PDA = G.pda()
        _str = 'PDA by Step: '
        for step in npda.read_input_stepwise(sentence):
            _str += str(step) + '\n'
        return _str, None
    
    if operation == "NPDA接受句子":
        C = CFG()
        C.loadFromVariable(Input)
        G = Greibach()
        G._loadCFG(C.__copy__())
        G._reduceCFG()
        G._removeLeftRecursion()
        G._removeNullProductins()
        G._removeUnitProductins()
        G._terminateFirstSymbol()
        G._renameCFG()
        npda, PDA = G.pda()
        print(npda.accepts_input(sentence))
        if npda.accepts_input(sentence):
            return '接受句子', None
        else:
            return '不接受句子', None
    
    

demo = gr.Interface(
    fn=visual,
    inputs=[
        gr.Textbox(lines=15, placeholder="按照如下格式输入产生式...\n \
                   V: (非终结符) \n \
                   SIGMA: (终结符)\n \
                   S: (初始符号)\n \
                   P: (产生式)"),
        gr.Radio(["消除无用符号", "消除左递归", "消除空产生式", "消除单一产生式", \
                  "生成Greibach范式", "Greibach范式验证", "PDA规则生成", "NPDA接受句子", "PDA单步运行"]),
        
        gr.Textbox(lines=1, placeholder="NPDA识别的句子..."),
    ],
    outputs=[
        gr.Textbox(lines=25, placeholder="输出结果..."),
        gr.Textbox(lines=1, placeholder="是否是格里巴克范式...")
    ],
)
demo.launch(share=True)


