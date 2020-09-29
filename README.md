# TwitterMapReduce
Projeto de SD da Universidade Católica de Pernambuco.
 **O projeto foi adaptado de uma busca com o Tweepy**
>Utilizei Hadoop 2.10 e Python 3

Como inicializar o Hadoop e fazer o MapReduce:\
Abre o prompt como ADM\
cd C:\Users\Jenni\Desktop\rabbitmq\twitter_search (para o diretório do seu arquivo)\
start-all.cmd

hadoop fs -mkdir /input_dir\
hadoop fs -put C:/Users/Jenni/Desktop/rabbitmq/Twitter_search/input.txt /input_dir\
hadoop fs -ls /input_dir/\
hadoop dfs -cat /input_dir/input.txt

roda o mapreduce (FUNCIONA):\
hadoop jar c:/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.10.0.jar -file mapper.py -mapper "python mapper.py" -file reducer.py -reducer "python reducer.py" -input /in/input.txt -output /output

ver o que gerou\
hadoop dfs -cat /output_dir/*

remove arquivo do HDFS\
hadoop fs -rm -r /input_dir/input.txt

deleta o diretório input do HDFS\
hadoop fs -rm -r /input_dir

para os servidores yarn e dfs\
stop-all.cmd

sair do safemode\
hadoop dfsadmin –safemode leave
