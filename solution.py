import search
from copy import deepcopy

class State:
    def __init__(self):
        self.not_done_legs = []
        self.plane = {}
    def __lt__(self,obj):
        return True
        
class ASARProblem(search.Problem):

    def __init__(self):
        # self.state é um objecto da classe State
        self.state = State()
        self.airport = {}
        self.legs = {}
        
    def actions(self, state):
        actions_list = []
        
        for code in state.plane:
            # Se um avião ainda não realizou um voo, ele pode fazer qualquer uma das legs não feitas
            if (len(state.plane[code]['legs']) == 0): 
                for leg in state.not_done_legs:
                    actions_list.append((code,leg[0],leg[1]))
            # Se o avião já realizou voos, ele só pode partir do aeroporto de chegada da última leg
            else : 
                next_dep = state.plane[code]['legs'][-1][2]
                # Procura legs not done que partam do aeroporto onde o avião chegou na leg anterior
                for item in state.not_done_legs:
                    if (next_dep == item[0]):
                        actions_list.append((code,item[0],item[1]))

        return actions_list

    def result(self, state, action):
        state1 = deepcopy(state)
        # Põe valores de action (código de avião, aeroporto de chegada e aeroporto de partida em 
        # variáveis locais)
        code = action[0]
        a_partida = action[1]
        a_chegada = action[2]

        # Caso seja o primeiro voo a ser feito por este avião, ready_to_fly_time = hora de abertura do aeroporto

        if (len(state1.plane[code]['legs']) == 0): 
            state1.plane[code]['ready_to_fly_time'] = self.airport[a_partida]['start']
        # Vê se avião quer partir de um aeroporto que ja fechou
        # O compare_time retorna true se o primeiro tempo for mais tarde que o segundo
        if (compare_time(state1.plane[code]['ready_to_fly_time'],self.airport[a_partida]['end']) == False):
            tempo_chegada = soma_time(self.legs[(a_partida,a_chegada)]['flight_duration'], state1.plane[code]['ready_to_fly_time'])   
            # Vê se o avião está a chegar a um aeroporto que ainda nao abriu
            if (compare_time(tempo_chegada, self.airport[a_chegada]['start']) == False):
                # Para o caso em que o avião chega a um aeroporto que não abriu, temos de atrasar a partida do mesmo
                state1.plane[code]['ready_to_fly_time'] = soma_time(time_dif(tempo_chegada,self.airport[a_chegada]['start']),state1.plane[code]['ready_to_fly_time'])
                tempo_chegada = soma_time(self.legs[(a_partida,a_chegada)]['flight_duration'], state1.plane[code]['ready_to_fly_time'])
            # Este if é parecido ao anterior, porque os aviões que chegavam cedo ao aeroporto 
            # tinham de partir mais tarde. Para mudar a hora de partida é preciso recalcular o 
            # ready_to_fly_time e o tempo_chegada. Uma vez recalculdados temos de comparar de novo
            # com a abertura do aeroporto de destino. Decidiu-se fazer um if/else dentro de um loop,
            # visto que depois de recalculado o tempo de chegada será sempre depois da abertura do
            # aeroporto de destino. Força-se o return state para salvaguardar contra o caso da 
            # função não retornar nada, o que faria a função retornar NoneType.
            if (compare_time(tempo_chegada, self.airport[a_chegada]['start']) == True):
                # Caso em o avião chega ao aeroporto depois de estar fechado
                if (compare_time(tempo_chegada, self.airport[a_chegada]['end'])): 
                    return state
                # Caso em que nenhuma das restrições anteriores se verifica
                else: 
                    state1.plane[code]['legs'].append((state1.plane[code]['ready_to_fly_time'],a_partida,a_chegada))
                    state1.plane[code]['ready_to_fly_time'] = soma_time(tempo_chegada,state1.plane[code]['rot_time'])
                    state1.not_done_legs.remove((a_partida,a_chegada))
                    return state1
            else:
                return state
        else:
            return state

    # Considerou-se como goal_state o estado em que não há nenhuma leg por fazer, 
    # e em que para todos os aviões a partida da primeira leg é igual à chegada da última
    def goal_test(self, state):
        if (len(state.not_done_legs) == 0):
            for code in state.plane:
                if (len(state.plane[code]['legs']) != 0):
                    if (state.plane[code]['legs'][0][1] != state.plane[code]['legs'][-1][2]):
                        return False
            
            return True
        return False
    
    # O custo de cada ação é o lucro máximo da leg a subtrair pelo lucro feito se for uma certa
    # classe a fazer esta leg. O custo pode, em certos casos, ser igual a 0.
    def path_cost(self, c, state1, action, state2):
        # Põe valores de action (código de avião, aeroporto de chegada e aeroporto de partida em 
        # variáveis locais)
        code = action[0]
        a_partida = action[1]
        a_chegada = action[2]

        # Profit da leg efetuada por determinada classe de avião
        profit = float(self.legs[(a_partida,a_chegada)][self.state.plane[code]['classe']])
        max_profit = self.legs[(a_partida,a_chegada)]['max_profit']
        return max_profit-profit+c
                
    def heuristic(self, node):
        #note: use node.state to access the state
        return 0 
        
    def load(self, fh):
        # note: fh is an opened file object
        # Cria 2 dicionários vazios 
        plane, classe = ({} for i in range(2)) 

        # Iteração das linhas do ficheiro
        for line in fh:
            # Tira os espaços
            line_list = line.split()

            # Se for uma linha vazia, line_list vai ser uma lista vazia
            if(len(line_list) == 0):
                continue
                # Se a linha for um aeroporto, cria um dicionário dentro do dicionário airport,
                # cuja chave do segundo é o code do aeroporto e o item, correspondente a essa chave,
                # é um dicionário com duas chaves, start (opening time) e end (closing time) e os
                # items correpondentes, lidos do ficheiro
            elif(line_list[0] == 'A'):
                self.airport[line_list[1]]={}
                self.airport[line_list[1]]['start'] = line_list[2]
                self.airport[line_list[1]]['end'] = line_list[3].rstrip() # Remove \n final
                # Se a linha for um avião, adiciona a chave do modelo do avião ao dicionário
                # plane, em que o item é a classe a que o avião pertence"""
            elif(line_list[0] == 'P'):           
                plane[line_list[1]] = line_list[2].rstrip()
                # Se a linha for uma classe de avião, adiciona a chave do tipo de classe ao 
                # dicionário classe, em que o item correspondente é o rotation time
            elif(line_list[0] == 'C'):
                classe[line_list[1]] = line_list[2].rstrip()
            # Linha é uma leg
            elif(line_list[0] == 'L'):
                profit = 0
 
                # Cria um dicionário dentro do dicionário legs, em que a chave do segundo
                # é um tupple, com o aeroporto de partida e chegada, e a chave do primeiro é a
                # flight_duration, cujo item correspondente é o valor lido do ficheiro
                self.legs[(line_list[1],line_list[2])] = {}
                self.legs[(line_list[1],line_list[2])]['flight_duration'] = line_list[3]
               
                # Adiciona à lista de legs ainda não realizadas o tupple com o aeroporto de 
                # partida e chegada
                self.state.not_done_legs.append((line_list[1],line_list[2]))

                # Na linha da leg itera sobre as classes que podem fazer essa leg
                for i in range(4,len(line_list),2):
                    # Acrescenta ao segundo dicionário a chave da classe, em que o item 
                    # correspondente é o profit da mesma, lido do ficheiro
                    self.legs[(line_list[1],line_list[2])][line_list[i]] = line_list[i+1].rstrip()
                    # Seleciona o maior profit de todos os profits, de todas as classes
                    if(float(line_list[i+1]) > profit):
                        profit = float(line_list[i+1])
                
                # Adiciona ao segundo dicionário a chave max_profit, com o profit máximo nessa leg
                self.legs[(line_list[1],line_list[2])]['max_profit'] = profit

        # Cria um dicionário dentro do dicionário plane, em que a chave do segundo é o codigo
        # de registo do avião, e as chaves do primeiro são a classe, cujo item é retirado a partir 
        # do dicionário plane (variável local da função); o rot_time, cujo item é retirado a 
        # partir do dicionário classe; ready_to_fly_time, inicializado com a string '0000';
        # legs, cujo item é uma lista vazia, a ser usada posteriormente
        for code in plane:
            self.state.plane[code]={}
            self.state.plane[code]['classe'] = plane[code]
            self.state.plane[code]['rot_time'] = classe[plane[code]]
            self.state.plane[code]['legs'] = []

        # Copia os valores internos de state para initial
        self.initial = deepcopy(self.state)
    
    def save(self, fh, state):
        # note: fh is an opened file object
        # Se o problema não é resolvível apenas escreve Infeasible no ficheiro
        if (state == None):
            fh.write('Infeasible\n')
        else:
            profit = 0
            for model in state.plane:
                # Só escreve o schedule de um avião, se ele voar alguma leg
                if(len(state.plane[model]['legs']) > 0):
                    linha ='S '

                    linha = linha + model
                    # Imprime as legs
                    for leg in state.plane[model]['legs']:
                        # Para cada leg imprime aeroporto de partida, chegada e duração do voo
                        linha = linha + ' ' + leg[0] + ' ' + leg[1] + ' ' + leg[2]
                        # Profit máximo calculado pelo algoritmo de procura
                        profit = profit + float(self.legs[(leg[1],leg[2])][self.state.plane[model]['classe']])

                    fh.write(linha + '\n')
                    
            fh.write('P ' + str(profit) + '\n')

# Função que soma dois tempos
def soma_time(time1,time2):
    time1_minute = int(time1[2:])
    time2_minute = int(time2[2:])
    time1_hour = int(time1[:2])
    time2_hour = int(time2[:2])
    
    time3_minute = time1_minute + time2_minute
    time3_hour = int(0)
    
    if (time3_minute >= 60):
        time3_hour = time3_hour + int(time3_minute/60)
        time3_minute = time3_minute % 60

    time3_hour = time3_hour +  time1_hour + time2_hour

    return create_time_string(time3_hour,time3_minute)

# Função que calcula a diferença de tempo entre dois tempos, o segundo argumento tem de ser o 
# maior
def time_dif(time_m, time_M):
    minute_m = int(time_m[2:])
    minute_M = int(time_M[2:])
    hour_m = int(time_m[:2])
    hour_M = int(time_M[:2])

    if(minute_M == minute_m):
        minute_s = 0
        hour_s = hour_M - hour_m
    if(minute_M > minute_m):
        minute_s = minute_M - minute_m
        hour_s = hour_M - hour_m
    if(minute_M < minute_m):
        minute_s = minute_M - minute_m + 60
        hour_m = hour_m + 1
        hour_s = hour_M - hour_m 

    return create_time_string(hour_s,minute_s) 

# Função que cria a string do tempo usada para guardar o tempo de partida, o tempo de chegada e o
# ready_to_fly_time, etc
def create_time_string(h,m):
    hour = str(h)
    minuto = str(m)
    
    if(len(hour) == 1):
        hour = str('' + '0' + hour)
    if(len(minuto) == 1): 
        minuto = str('' + '0' + minuto)
    if(len(hour) == 2 and len(minuto) == 2):
        return hour + minuto
    else: 
        return create_time_string(hour,minuto)

# Compara dois tempos, para ver qual é o maior, retorna true se o primeiro argumento for mais 
# tarde que o segundo
def compare_time(time1,time2):
    time1_minute = int(time1[2:])
    time2_minute = int(time2[2:])
    time1_hour = int(time1[:2])
    time2_hour = int(time2[:2])

    if (time1_hour > time2_hour):
        return True

    if (time1_hour == time2_hour and time1_minute >= time2_minute) : 
        return True   

    return False