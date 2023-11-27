import re
from itertools import product
import sys
from automata.pda.npda import NPDA


class CFG:
    """ Context Free Gramamr Class """
    # Variables - Non Terminal Symbols
    _V = []
    # Alphabet - Terminal Symbols
    _SIGMA = []
    # Start Symbol
    _S = None
    # Productions
    _P = []
    

    def loadFromFile(self, txtFile):
        """ Costructor From File """
        with open(txtFile) as f:
            lines = f.readlines()
        g = ''.join([re.sub(" |\n|\t", "", x) for x in lines])
        v = re.search('V:(.*)SIGMA:', g).group(1)
        sigma = re.search('SIGMA:(.*)S:', g).group(1)
        s = re.search('S:(.*)P:', g).group(1)
        p = re.search('P:(.*)', g).group(1)
        self.load(v, sigma, s, p)

    def loadFromVariable(self, text):
        """ Costructor From File """
        g = ''.join([re.sub(" |\n|\t", "", x) for x in text])
        v = re.search('V:(.*)SIGMA:', g).group(1)
        sigma = re.search('SIGMA:(.*)S:', g).group(1)
        s = re.search('S:(.*)P:', g).group(1)
        p = re.search('P:(.*)', g).group(1)
        self.load(v, sigma, s, p)

    def load(self, v, sigma, s, p):
        """ Costructor From Strings """
        self._V = [re.escape(x) for x in re.split(',', v.replace(" ", ""))]
        self._SIGMA = [re.escape(x) for x in re.split(',', sigma.replace(" ", ""))]
        if [x for x in self._V if x in self._SIGMA]:
            sys.exit('Error : V intersection SIGMA is not empty')
        s = re.escape(s.replace(" ", ""))
        if s in self._V:
            self._S = s
        else:
            sys.exit('Error : start symbol is not in V')
        p = p.replace(" ", "")
        self._P = self._parsProductions(p)

    def _parsProductions(self, p):
        """ Productions Builder """
        P = {}
        v = []
        self.symbols = self._V + self._SIGMA
        rows = re.split(',', p)
        for row in rows:
            item = re.split('->', row)
            left = re.escape(item[0])
            if (left in self._V):
                v.append(left)
                P[left] = []
                rules = re.split('\|', item[1])
                for rule in rules:
                    P[left].append(self._computeRule(rule))
            else:
                raise ImportError('Rigth simbol in production ' + row + ' is not in V')
        if [True] * len(self._V) == [x in self._V for x in v]:
            return P
        else:
            raise ImportError('Error : not all vocabulary has been used : ' + ''.join([x for x in self._V if x not in v]))

    def _computeRule(self, rule):
        """ Single Rule Builder"""
        _rule = rule
        rules = {}
        i = 0
        while len(_rule) > 0:
            r = re.search('|'.join(self.symbols), rule)
            if r.start() == 0:
                rules[i] = re.escape(_rule[0:r.end()])
                _rule = _rule[r.end():]
                i += 1
            else:
                raise ImportError('Error : undefined symbol find in production : ' + _rule)
        return rules

    def __copy__(self):
        """ Copy Costructor """
        return CFG().create(self._V, self._SIGMA, self._S, self._P)

    def create(self, v, sigma, s, p):
        """ Static Costructor """
        newCFG = CFG()
        newCFG._V = v
        newCFG._SIGMA = sigma
        newCFG._S = s
        newCFG._P = p
        return newCFG

    def __str__(self, order=False):
        _str = 'V: ' + ', '.join(self._V) + '\n'
        _str += 'SIGMA: ' + ', '.join(self._SIGMA) + '\n'
        _str += 'S: ' + self._S + '\n'
        _str += 'P:'
        if order:
            V = [x for x in order if x in self._V] + [x for x in self._V if x not in order]
        else:
            V = self._V
        for v in V:
            _str += '\n\t' + v + ' ->'
            _PS = []
            for p in self._P[v]:
                _p = ''
                for i, s in p.items():
                    _p += ' ' + s
                _PS.append(_p)
            _str += ' |'.join(_PS)
        return _str.replace('\\', '')
    



class Greibach(object):
    def isInNF(self, cfg):
        """ A -> a | a A_1 ... A_n"""
        if re.escape('#') in cfg._SIGMA:
            return False
        else:
            for v, PS in cfg._P.items():
                for p in PS:
                    if p[0] in cfg._V:   #如果右部打头的是非终结符
                        return False
                    elif len(p) > 1:
                        for i in range(1, len(p)): 
                            if p[i] not in cfg._V:  #如果右部后面不是非终结符
                                #print(p, i, cfg._V)
                                return '不是Greibach范式'
        return '是Greibach范式'
    


    def _loadCFG(self, cfg):
        self._V = [x for x in cfg._V]
        self._SIGMA = [x for x in cfg._SIGMA]
        self._S = cfg._S
        self._P = {}
        for v, p in cfg._P.items():
            self._P[v] = []
            for el in p:
                _p = {}
                for i, s in el.items():
                    _p[i] = s
                self._P[v].append(_p)
    


    def _reduceCFG(self):
        W = {}
        W[0] = self._updateW(self._SIGMA)
        i = 1
        W[i] = self._updateW(W[i - 1], W[i - 1])
        while (W[i] != W[i - 1]):
            i += 1
            W[i] = self._updateW(W[i - 1], W[i - 1])
        V = W[i]
        _P = {}
        for v in V:
            _P[v] = []
            for _p in self._P[v]:
                if [True for x in range(len(_p))] == [x in V + self._SIGMA for n, x in _p.items()]:
                    _P[v].append(_p)
        self._P = _P
        Y = {}
        Y[0] = [self._S]
        j = 1
        Y[1] = self._propagateProduction(Y[0])
        while (Y[j] != Y[j - 1]):
            j += 1
            Y[j] = self._propagateProduction(Y[j - 1], Y[j - 2])
        self._V = [x for x in V if x in Y[j]]
        self._SIGMA = [x for x in self._SIGMA if x in Y[j]]

    def _updateW(self, SET, _prev=None):
        if _prev is not None:
            W = [x for x in _prev]
        else:
            W = []
        for v in self._P:
            for p in self._P[v]:
                for n, _v in p.items():
                    if _v in SET and v not in W:
                        W.append(v)
        return W
    
    def _propagateProduction(self, Y, _prev=None):
            _y = [x for x in Y]
            y = [x for x in Y if x not in self._SIGMA]
            if _prev is not None:
                y = [x for x in y if x not in _prev]
            for v in y:
                for p in self._P[v]:
                    for n, s in p.items():
                        if s not in Y:
                            _y.append(s)
            return _y
    


    def _removeNullProductins(self):
        if re.escape('#') not in self._SIGMA:
            return
        #print("before", self._SIGMA)
        self._SIGMA = [x for x in self._SIGMA if '#' not in x]
        #print("after", self._SIGMA)
        _P = {}
        for v in self._V:
            if v not in _P.keys():
                _P[v] = []
            for p in self._P[v]:
                if len(p) == 1 and p[0] == re.escape('#'):  #找到空产生式
                    newPs = self._createProductions(v)      #当前非终结符v有空产生式，处理
                    for _v, _p in newPs.items():
                        if _v not in _P.keys():
                            _P[_v] = []
                        _P[_v] = [x for x in _p if x not in _P[_v]] + _P[_v]
                else:
                    _P[v] = [x for x in [p] if x not in _P[v]] + _P[v]
        self._P = _P

    def _createProductions(self, s):
        _P = {}
        for v in self._V:
            for p in self._P[v]:
                if s in p.values():
                    if len(p.values()) > 1:
                        # generate all possible combination
                        i = list(p.values()).count(s)
                        cases = [[x for x in l] for l in list(product([True, False], repeat=i))]
                        # [Treu]*i means that all ss do not change eg. s=B, V->aBa remain aBa
                        cases = [x for x in cases if x != [True] * i]
                        for case in cases:
                            k = 0  # production length
                            _i = 0  # number of s appeared
                            c = {}
                            for key, val in p.items():
                                if val != s:
                                    c[k] = val
                                    k += 1
                                elif case[_i]:
                                    c[k] = val
                                    k += 1
                                    _i += 1
                                else:
                                    _i += 1
                            if v not in _P.keys():
                                _P[v] = []
                            _P[v] = [x for x in [c] if x not in _P[v] and x != {}] + _P[v]
                    else:
                        # this mean that v -> p is equl to v -> #
                        newPs = self._createProductions(v)
                        for _v, _p in newPs.items():
                            if _v not in _P.keys():
                                _P[_v] = []
                            _P[_v] = [x for x in _p if x not in _P[_v]] + _P[_v]
        return _P
    


    def _removeUnitProductins(self):
        P = {}
        for v in self._V:
            P[v] = []
            for p in self._P[v]:  #遍历的是单个产生式
                if len(p) == 1 and p[0] in self._V:  #如果是单产生式
                    newPs = self._findTerminals(v, p[0])    #v左部  p[0]右部
                    P[v] = [x for x in newPs if x not in P[v]] + P[v]  #如果是单产生式就替换，
                else:                                                  #如果不是就加入原来的产生式
                    P[v] = [x for x in [p] if x not in P[v]] + P[v]
        self._P = P
        self._reduceCFG()           #判断是否产生了不可达产生式

    def _findTerminals(self, parent, son):
        T = []
        for p in self._P[son]: 
            if len(p) > 1 or p[0] in self._SIGMA:
                T = [x for x in [p] if x not in T] + T
            elif p[0] != parent:
                T = [x for x in self._findTerminals(parent, p[0]) if x not in T] + T
        return T
    


    def _removeLeftRecursion(self):
            new_P = self._converter2list(self._P)
            eliminate_indirect = self._eliminate_indirect(new_P)
            eliminate_direct = self._eliminate_direct(eliminate_indirect)
            result = self._converter2map(eliminate_direct)
            new_V = []
            for v, _ in result.items():
                new_V.append(v)
            self._V = new_V
            for _, p in result.items():
                for value in p:
                    for _, id in value.items():
                        if (id not in self._SIGMA) and (id not in self._V):
                            self._SIGMA.append(id)
            #print("sigma: ", self._SIGMA)
            #print("v", self._V)
            self._P = result

    def _newVariable(self, name_list, S):
        i = 0
        while (S + '_' + str(i) in name_list):
            i += 1
        name_list.append(S + '_' + str(i))
        return S + '_' + str(i)

    def _converter2list(self, P):
        new_P = {}
        for v, p in P.items():
            new_P[v] = []
            for value in p:
                str = ''
                for i, id in value.items():
                    str += id
                new_P[v].append(str.replace('\\', ''))
        return new_P

    def _converter2map(self, P):
        new_P = {}
        for v, p in P.items():
            new_P[v] = []
            for value in p:
                if value[0] == '#' and len(value) != 1:
                    value = value[1:]
                new_dic = {}
                count = 0
                i = 0
                while(i < len(value)):
                    #print("before: ", value[i])
                    if i+1<len(value) and value[i+1] != '_':
                        new_dic[count] = re.escape(value[i])
                        #print("not _ :", value[i])
                        i += 1
                    else:
                        new_dic[count] = re.escape(value[i:i+3])
                        #print("is _ :", value[i:i+3])
                        i += 3
                    count += 1
                new_P[v].append(new_dic)
        return new_P

    def _eliminate_indirect(self, map):
        i = 0
        j = 0
        for key, value in map.items() :   #key是非终结符，value是list
            for key1, value1 in map.items() :
                if j > i :
                    for v in value1 :       #遍历右部每条产生式
                        if v[0] == key :    #如果发现左递归
                            vv = v[1:]
                            new_values = []
                            for v1 in value :
                                new_values.append(v1+vv)  #加入的是没有左递归的产生式
                            value1 += new_values
                            value1.remove(v)            
                j+=1
            i+=1
            j=0            
        #print(map)                       
        return map

    def _eliminate_direct(self, map):
        name_list = []
        newRules = {}
        exist = False
        for key,value in map.items():
            for v in value :
                if v[0] == key :
                    exist = True
            if exist==False:
                newRules[key] = value 
            else :
                key1 = key
                #key2 = key+'\''
                key2 = self._newVariable(name_list, key)
                value1 = []
                value2 = [] 
                for v in value :
                    if v[0] != key:
                        value1.append(v+key2)
                    else :
                        value2.append(v[1:]+key2)    
                value2.append('#')
                newRules[key1] = value1
                newRules[key2] = value2
            exist = False    
        #print(newRules)        
        return newRules 



    def _terminateFirstSymbol(self):
        _P = {}
        for v in self._V:
            _P[v] = []
            for p in self._P[v]:        #遍历所有产生式
                if p[0] in self._V:
                    newPs = self._terminateProduction(p)    #最终返回来的终结符打头的产生式
                    _P[v] = [x for x in newPs if x not in _P[v]] + _P[v]
                else:
                    _P[v].append(p)
        self._P = _P

    def _terminateProduction(self, p): #输入的是 Cca 把C换完传回来
        _Ps = []
        for _p in self._P[p[0]]:        #左部是非终结符的产生式，现在遍历的是C的产生式
            if _p[0] in self._V:        #如果C的产生式打头还是非终结符
                T = self._terminateProduction(_p)   #继续递归
            else:
                T = [_p]
            for t in T:
                new = {}
                for i in range(len(t)):
                    new[i] = t[i]
                i = len(new) - 1
                for j in range(1, len(p)):
                    new[i + j] = p[j]
                _Ps.append(new)
        return _Ps
    
    def _renameCFG(self):
        T = self._V
        new_P = {}
        _P = {}
        
        for v, p in self._P.items():
            _P[v] = []
            for value in p:
                new_value = {}
                for i, id in value.items():
                    if i != 0 and id in self._SIGMA:
                        if id not in new_P.values():
                            new_name = self._newVariable(T, id.upper())
                            new_value[i] = new_name
                            new_P[new_name] = id
                        else:
                            name = ''
                            for n in new_P:
                                if new_P[n] == id:
                                    name = n
                            new_value[i] = name
                    else:
                        new_value[i] = id
                _P[v].append(new_value)
        
        #self._V += list(new_P.keys())
        new = {}
        for v, p in new_P.items():
            new[v] = []
            new[v].append({0:p})
        _P.update(new)
        #print("_P: ",_P)
        self._P.update(_P)
        #print("_P: ",self._P)

    
    def _convert2PDA(self):
        PDA = {}
        PDA['states'] = {'q0', 'q1', 'q2'}
        PDA['input_symbols'] = set(self._SIGMA)
        PDA['stack_symbols'] = set(self._V + ['#'])
        PDA['initial_state'] = 'q0'
        PDA['initial_stack_symbol'] = '#'
        PDA['final_states'] = {'q2'}
        PDA['acceptance_mode'] = 'final_state'
        PDA['transitions'] = {
            'q0': {
                '': {
                    '#': {('q1', ('S', '#'))}  # no change to stack
                }
            },
            'q1': {
                '': {
                    '#': {('q2', '#')}  # push '#' to (currently empty) stack
                }  
            }
        }

        new_rule = {}
        for sigma in self._SIGMA:
            new_rule[sigma] = {}
            for v, p in self._P.items():
                new_rule[sigma][v] = set()
                for value in p:
                    if sigma in value.values():
                        if len(value) == 1:
                            new_rule[sigma][v].add(('q1',''))
                        else: 
                            stack = []
                            for i, id in value.items():
                                if i != 0:
                                    stack.append(id)
                            #print("stack: ", tuple(stack))
                            new_rule[sigma][v].add(('q1',tuple(stack)))
                if new_rule[sigma][v] == set():
                    del new_rule[sigma][v]
        
        PDA['transitions']['q1'].update(new_rule)
        #print(PDA['transitions'])
        npda = NPDA(
            states=PDA['states'],
            input_symbols=PDA['input_symbols'],
            stack_symbols=PDA['stack_symbols'],
            transitions=PDA['transitions'],
            initial_state=PDA['initial_state'],
            initial_stack_symbol=PDA['initial_stack_symbol'],
            final_states=PDA['final_states'],
            acceptance_mode=PDA['acceptance_mode']
        )

        return npda, PDA
    
    def printPDA(self, PDA):
        _str = 'Q:  ' + ', '.join(list(PDA['states'])) + '\n'
        _str += 'SIGMA:  ' + ', '.join(list(PDA['input_symbols'])) + '\n'
        _str += 'T:  ' + ', '.join(list(PDA['stack_symbols'])) + '\n'
        _str += 'F:  ' + ', '.join(list(PDA['final_states'])) + '\n'
        for fst in PDA['transitions']:
            for sec in PDA['transitions'][fst]:
                for third, value in PDA['transitions'][fst][sec].items():
                    _str += "delta("+fst+", "+sec+", "+third+")" + "  =  "+str(value) + '\n'
        return _str



    def __str__(self, order=False):
        _str = 'V:  ' + ', '.join(self._V) + '\n'
        _str += 'SIGMA:  ' + ', '.join(self._SIGMA) + '\n'
        _str += 'S:  ' + self._S + '\n'
        _str += 'P: '
        if order:
            V = [x for x in order if x in self._V] + [x for x in self._V if x not in order]
        else:
            V = self._V
        for v in V:
            _str += '\n\t' + v + ' ->'
            _PS = []
            for p in self._P[v]:
                _p = ''
                for i, s in p.items():
                    _p += ' ' + s
                _PS.append(_p)
            _str += ' |'.join(_PS)
        return _str.replace('\\', '')



    def greibach(self, cfg):
        self._loadCFG(cfg)
        self._reduceCFG()
        self._removeLeftRecursion()
        self._removeNullProductins()
        self._removeUnitProductins()
        self._terminateFirstSymbol()
        self._renameCFG()
        return CFG().create(self._V, self._SIGMA, self._S, self._P)
    
    def pda(self):
        npda, PDA = self._convert2PDA()
        return npda, PDA


if __name__ == "__main__":
    cfg_path = r"tests/Simpletest1.txt"
    C = CFG()
    #C.loadFromFile(cfg_path)
    text = 'V : \
        S,A,B,C \
    SIGMA: \
        a,b,c,# \
    S: S \
    P : \
        S -> aAbBC, \
        A -> aA | B | #,  \
        B -> bcB | Cca,  \
        C -> aC | c  '
    C.loadFromVariable(text)

    G = Greibach()
    G.greibach(C.__copy__())

    npda, PDA = G.pda()
    print(G.printPDA(PDA))

    _str = 'PDA by Step: '
    for step in npda.read_input_stepwise('abccac'):
        _str += str(step) + '\n'
    print(_str)
    """ my_input_str = 'abccac'
    if npda.accepts_input(my_input_str):
        print('accepted')
    else:
        print('rejected')
    print() """

    """ print("before is Greibach? ", G.isInNF(C))
    print("after is Greibach? ", G.isInNF(G))
    print(' - Input')
    print(G._P)
    print(' - Output') """