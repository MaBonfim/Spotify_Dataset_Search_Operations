#Nomes: Matheus Bonfim da Rocha - Samuel Felipe Cordova Victorio
#Data: 06/12/2023
# Programa para busca de registros com uso de indice secundario do arquivo de musicas "tracks_features.csv" do spotify

#------------IMPORTS----------------------------------
import csv
import sys
#-----------------------------------------------------
#------------------------------------------------------
class IndiceSecundario():
	#Atributos----------------------------
	#-------------------------------------
	__arquivoQuery = None 					#arquivo de entrada
	__arquivoSaida = None 					#arquivo de saida
	__arquivoDados = None 					#arquivo e dados

	__listaTabelaIndiceSecundario = [] 		#lista que possui tabelas de cada indice secundario
	__tabelaCamposChaveSecundaria = [] 		#lista de tuplas que possuem (campo,indice do campo no registro)
	__operacoesAndOr = [] 					#lista que guarda as operações do arquivo de entrada
	__tuplasCampos = []						#lista de tuplas dos campos que vieram do arquivo de entrada
	__valoresCampos = [] 					#lista com valores referentes a cada campo do arquivo de entrada
	__listaOcorrenciasTabelas = [] 			#lista com lista de ocorrencias de cada tabela de idx secundario
	__tabelaIndicePrimario = []				#tabela de indice primario

	#construtor-----------------------
	#-----------------------------
	def __init__(self,nomeArqDados,nomeArqEntrada,nomeArqSaida):

		self.__arquivoDados = open(nomeArqDados, "r+", encoding="utf-8")
		self.__arquivoSaida = open(nomeArqSaida,"w",encoding="utf-8")
		self.__arquivoQuery = open(nomeArqEntrada,"r+",encoding="utf-8")

		
		print("Verificando arquivos de entrada")
		self.defineCampos()
		self.defineOperacoes()

		print("Criando tabelas de indice")
		self.defineTabelasDeIndices()

		print("Definindo listas de ocorrencias")
		self.defineListasOcorrencias()

		print("Realizando operacoes de busca")
		listaFinal = self.defineListaFinal()

		print("Escrevendo arquivo de saida")
		self.escreveArquivoSaida(listaFinal)

	#---------------------------------------------------------------------
	#---------------------------------------------------------------------

	#-----METODOS DE VERIFICACAO DE ARQUIVOS-------------------------
	#define listas contendo os campos para busca, os valores desses campos e os operadores booleanos de busca
	def defineOperacoes(self):
		self.__arquivoQuery.seek(0,0)
		linha = self.__arquivoQuery.readline()[:-1]
		if len(linha) == 0:
			print("Arquivo vazio")
			self.escreveArquivoSaida(0,"Arquivo vazio")
			return -1
		
		
		campos = linha.split(' ')
		for i in range(0,len(campos)):
			#parte impar sao os nomes dos campos
			if i % 2 == 0:
				#guarda em uma lista de tuplas usado na criação dos arquivos de indice secundario
				a = self.getTuplaCampo(campos[i])
				if a == (0,0):
					print("Arquivo invalido")
					self.escreveArquivoSaida(0,"Arquivo invalido")
					return -1
				self.__tuplasCampos.append(a)
			#parte par sao os & ou ||
			else:
				#guarda em uma lista com as operacoes
				if(campos[i] == "&" or campos[i] == "||"):
					self.__operacoesAndOr.append(campos[i])
				else:
					print("Arquivo invalido")
					self.escreveArquivoSaida(0,"Arquivo invalido")
					return -1
		#le a ultima linha do arquivo de entrada
		#le cada um dos valores da ultima, os valores que nao sao o primeiro tem um espaco no comeco
		linha = self.__arquivoQuery.readline()
		valores = linha.split(',')

		#se a quantidade de valores de busca for diferente dos campos de busca, o arquivo esta errado
		if len(valores) != len(self.__tuplasCampos):
			print("Arquivo invalido")
			self.escreveArquivoSaida(0,"Arquivo invalido")
			return -1
		
		#salva a lista com os valores de busca
		for i in range(0,len(valores)):
			if i == 0:
				self.__valoresCampos.append(valores[i])
				continue
			self.__valoresCampos.append(valores[i][1:])
		
		return 0
		#foram definidos tuplasCampos, operacoes e valoresCampos

	#faz a leitura da primeira linha do arquivo de dados e define uma lista de tuplas que possuem (<nome_campo>,<indice_no_registro_do_campo>)		
	def defineCampos(self):
		try:
			self.__arquivoDados.seek(0,0)
			linhaCampos = self.__arquivoDados.readline()[:-1]
			campos = linhaCampos.split(',')
			
			for i in range(0,23):
				if not(i == 1 or i == 2 or i == 4 or i == 6 or i == 7 or i == 8 or i == 11 or i == 13 or i == 22): continue
				self.__tabelaCamposChaveSecundaria.append((campos[i],i))
		except:
			print("Arquivo de dados incompativel")
			self.escreveArquivoSaida(0,"Arquivo de dados incompativel")
	
	#recebe um campo e verifica se ele é um dos campos válidos lidos do arquivo de dados
	def getTuplaCampo(self,campo):
		for i in self.__tabelaCamposChaveSecundaria:
			if i[0] == campo: return (i)
		return (0,0)
	#---------------------------------------------------------------------------		
	
	#-------METODO DE CRIACAO DAS TABELAS DE INDICE-----------------------------
	#cria a tabela de indice primario e as tabelas de indice secundario
	def defineTabelasDeIndices(self):
		contador = 0
		self.__arquivoDados.seek(0,0)
		
		for i in self.__tuplasCampos:
			self.__listaTabelaIndiceSecundario.append([])

		while True:
			posicao = self.__arquivoDados.tell()
			if not (line := self.__arquivoDados.readline()):
				break
			row = next(csv.reader([line]))
			chavePri = row[0]

			self.__tabelaIndicePrimario.append((chavePri,posicao))
			contador = 0
			for i in self.__tuplasCampos:
				chaveSec = row[i[1]]
				self.__listaTabelaIndiceSecundario[contador].append((chaveSec,chavePri))
				contador += 1

		self.__tabelaIndicePrimario.sort()
	#------------------------------------------------------------------------------
	
	#-----------METODOS DE OPERACOES DE BUSCA-------------------------------
	#para cada tabela de indice secundario verifica os registros que possuem o valor relacionado ao seu campo
	#as ocorrencias sao guardadas em uma lista de listas contendo as chaves primarias dos registros selecionados
	def defineListasOcorrencias(self):
		i = 0
		for tabelaIdxSec in self.__listaTabelaIndiceSecundario:
			ocorrencias = []
			for j in tabelaIdxSec:
				b = j[0].count(self.__valoresCampos[i])
				if b == 0: continue
				ocorrencias.append(j[1]) 
			i += 1
			self.__listaOcorrenciasTabelas.append(ocorrencias)

	#operacao and recebe duas listas de ocorrencias e retorna uma lista com as chaves presentes nas duas listas
	def operacaoAND(self,lista1,lista2):
		listaAux = []
		for i in lista1:
			for j in lista2:
				if i == j:
					listaAux.append(i)
					break
		lista1 = listaAux
		return lista1

	#operacao or recebe duas listas de ocorrencias e retorna a concatenacao delas
	def operacaoOr(self,lista1,lista2):
		for i in lista2:
			lista1.append(i)
		return lista1

	#realiza as operacoes com as listas de ocorrencias e retorna a lista final contendo as chaves primarias 
	def defineListaFinal(self):
		listaFinal = self.__listaOcorrenciasTabelas[0]
		tamanho = len(self.__listaOcorrenciasTabelas)
		if tamanho > 1:
			for i in range(1,tamanho):
				if self.__operacoesAndOr[i-1] == "&":
					listaFinal = self.operacaoAND(listaFinal,self.__listaOcorrenciasTabelas[i])
				elif self.__operacoesAndOr[i-1] == "||":
					listaFinal = self.operacaoOr(listaFinal,self.__listaOcorrenciasTabelas[i])
		return listaFinal

	#recebe uma chave e retorna o registro do arquivo de dados
	def pesquisaRegistroIdxPrimario(self, chave) :	
		inicio = 0
		fim = len(self.__tabelaIndicePrimario) - 1
		while inicio <= fim:
			meio = (inicio + fim) // 2
			valor_meio = self.__tabelaIndicePrimario[meio][0]

			if valor_meio == chave:
				endereco = int(self.__tabelaIndicePrimario[meio][1])
				self.__arquivoDados.seek(endereco,0)
				registro = self.__arquivoDados.readline()

				return registro
			elif valor_meio < chave:
				inicio = meio + 1  # Descarta a metade inferior.
			else:
				fim = meio - 1  # Descarta a metade superior.
		return False  # Se o elemento não estiver na lista.	
	#------------------------------------------------------------------------
	
	#--------------METODO DE ESCRITA DO ARQUIVO DE SAIDA------------------------------
	#recebe a lista de ocorrencias final contendo as chaves dos registros que serao escritos e as escrevem no arquivo de saida
	def escreveArquivoSaida(self,listaDeOcorrenciasFinal = 0,erro = 0):
		if erro == 0:
			if len(listaDeOcorrenciasFinal) == 0:
				self.__arquivoSaida.write("Nenhum resultado encontrado")

			for i in listaDeOcorrenciasFinal:
				self.__arquivoSaida.write(self.pesquisaRegistroIdxPrimario(i))
		else:
			self.__arquivoSaida.write(erro)
		
		print("Fechando arquivos")
		self.__del__()
		print("Fim do programa")
		sys.exit()
	#--------------------------------------------------------------------------------
	#desconstrutor
	def __del__(self):
		self.__arquivoDados.close()
		self.__arquivoQuery.close()
		self.__arquivoSaida.close()

#realiza a verificação dos parametros arqv
def verificaArgv(listaArgv):
	if len(listaArgv) != 4:
		print("Quantidade invalida de argumentos")
		return -1

	try:
		arq1 = open(listaArgv[1],"r",encoding="utf-8")
	except:
		print("Falha na abertura do arquivo de dados")
		return -1
	
	try:
		arq2 = open(listaArgv[2],"r",encoding="utf-8")
	except:
		print("Falha na abertura do arquivo de query")
		return -1

	arq1.close()
	arq2.close()
	return 0
	
if __name__ == "__main__":
    
	print("Verificando parametros de entrada")
	if verificaArgv(sys.argv) == -1: 
		print("Fim do programa")
		sys.exit()

	estrutura = IndiceSecundario(sys.argv[1],sys.argv[2],sys.argv[3])
	print("Fim do Programa")
	# destruir (chamado implicitamente pelo python)
	#estrutura.__del__()