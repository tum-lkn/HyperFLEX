Search.setIndex({envversion:46,filenames:["api","data","guicontroller","index","intelligence","management","modules","test","testcases"],objects:{"":{data:[1,0,0,"-"],guicontroller:[2,0,0,"-"],intelligence:[4,0,0,"-"],management:[5,0,0,"-"],test:[7,0,0,"-"],testcases:[8,0,0,"-"]},"data.config":{default_switch_ip_port:[1,4,1,""],default_switch_ip_prefix:[1,4,1,""],get_config_hyperflex_topo:[1,4,1,""],get_config_hyperflex_topo_simple:[1,4,1,""],get_default_controller_port:[1,4,1,""]},"data.dbinterfaces":{Controller:[1,3,1,""],Host:[1,3,1,""],HyperFlexTopoSimpleConnector:[1,3,1,""],Hypervisor:[1,3,1,""],IterMixin:[1,3,1,""],LogicalEdge:[1,3,1,""],LogicalEdgeEmbedding:[1,3,1,""],NetworkNode:[1,3,1,""],NetworkNodeInfo:[1,3,1,""],PhysicalEdge:[1,3,1,""],PhysicalPort:[1,3,1,""],PhysicalSwitch:[1,3,1,""],StoredNetworkNodeInfo:[1,3,1,""],StormConnector:[1,3,1,""],SwitchToVsdn:[1,3,1,""],Tenant:[1,3,1,""],Vsdn:[1,3,1,""],network_node_info_types:[1,5,1,""],register_network_node_info_type:[1,4,1,""]},"data.dbinterfaces.Controller":{"__storm_table__":[1,2,1,""],ip_port:[1,2,1,""],location:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.Host":{to_dictionary:[1,1,1,""],vsdn_id:[1,2,1,""]},"data.dbinterfaces.HyperFlexTopoSimpleConnector":{get_link:[1,1,1,""],get_network_node:[1,1,1,""],get_switch:[1,1,1,""],put_link:[1,1,1,""],put_network_node:[1,1,1,""],put_switch:[1,1,1,""],put_vsdn:[1,1,1,""],remove_link:[1,1,1,""],remove_network_node:[1,1,1,""],remove_switch:[1,1,1,""],remove_vsdn:[1,1,1,""]},"data.dbinterfaces.Hypervisor":{"__storm_table__":[1,2,1,""],status:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.IterMixin":{"__iter__":[1,1,1,""]},"data.dbinterfaces.LogicalEdge":{"__storm_table__":[1,2,1,""],id:[1,2,1,""],node_one:[1,2,1,""],node_one_id:[1,2,1,""],node_two:[1,2,1,""],node_two_id:[1,2,1,""],physical_embedding:[1,2,1,""],to_dictionary:[1,1,1,""],vsdn_id:[1,2,1,""]},"data.dbinterfaces.LogicalEdgeEmbedding":{"__storm_table__":[1,2,1,""],id:[1,2,1,""],logical_edge_id:[1,2,1,""],physical_edge_id:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.NetworkNode":{"__storm_table__":[1,2,1,""],"_info":[1,2,1,""],id:[1,2,1,""],info:[1,2,1,""],info_type:[1,2,1,""],ip:[1,2,1,""],name:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.NetworkNodeInfo":{network_node:[1,2,1,""]},"data.dbinterfaces.PhysicalEdge":{"__storm_table__":[1,2,1,""],id:[1,2,1,""],node_one_id:[1,2,1,""],node_two_id:[1,2,1,""],port_one:[1,2,1,""],port_one_id:[1,2,1,""],port_two:[1,2,1,""],port_two_id:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.PhysicalPort":{"__storm_table__":[1,2,1,""],id:[1,2,1,""],number:[1,2,1,""],speed:[1,2,1,""],switch_id:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.PhysicalSwitch":{"__storm_table__":[1,2,1,""],c_plane:[1,2,1,""],cplane:[1,2,1,""],dpid:[1,2,1,""],ip_port:[1,2,1,""],num_ports:[1,2,1,""],ports:[1,2,1,""],to_dictionary:[1,1,1,""]},"data.dbinterfaces.StoredNetworkNodeInfo":{network_node:[1,2,1,""],network_node_id:[1,2,1,""]},"data.dbinterfaces.StormConnector":{"__del__":[1,1,1,""],add_controller:[1,1,1,""],add_host:[1,1,1,""],add_logical_edge:[1,1,1,""],add_logical_link_embedding:[1,1,1,""],add_physical_edge:[1,1,1,""],add_physical_port:[1,1,1,""],add_physical_switch:[1,1,1,""],add_server:[1,1,1,""],config:[1,2,1,""],connection:[1,2,1,""],get_edges_by_node:[1,1,1,""],get_hypervisor:[1,1,1,""],get_network_nodes:[1,1,1,""],get_physical_topo:[1,1,1,""],get_vsdn:[1,1,1,""],remove_controller:[1,1,1,""],remove_host:[1,1,1,""],remove_logical_edge:[1,1,1,""],remove_logical_edge_embedding:[1,1,1,""],remove_physical_edge:[1,1,1,""],remove_physical_port:[1,1,1,""],remove_physical_switch:[1,1,1,""],remove_server:[1,1,1,""],remove_switch_to_vsdn:[1,1,1,""],remove_tenant:[1,1,1,""],remove_vsdn:[1,1,1,""],store:[1,2,1,""]},"data.dbinterfaces.SwitchToVsdn":{"__storm_table__":[1,2,1,""],id:[1,2,1,""],switch_id:[1,2,1,""],to_dictionary:[1,1,1,""],vsdn_id:[1,2,1,""]},"data.dbinterfaces.Tenant":{"__storm_table__":[1,2,1,""],id:[1,2,1,""],name:[1,2,1,""],to_dictionary:[1,1,1,""],vsdns:[1,2,1,""]},"data.dbinterfaces.Vsdn":{"__storm_table__":[1,2,1,""],"_hosts":[1,2,1,""],color:[1,2,1,""],controller:[1,2,1,""],controller_id:[1,2,1,""],get_hosts:[1,1,1,""],hypervisor:[1,2,1,""],hypervisor_id:[1,2,1,""],id:[1,2,1,""],logical_edges:[1,2,1,""],name:[1,2,1,""],subnet:[1,2,1,""],switches:[1,2,1,""],tenant_id:[1,2,1,""],to_dictionary:[1,1,1,""]},"guicontroller.config":{get_config:[2,4,1,""]},"guicontroller.guiclient":{ManagementGuiClient:[2,3,1,""]},"guicontroller.guiclient.ManagementGuiClient":{ServerAddress:[2,2,1,""],ServerPort:[2,2,1,""],Socket:[2,2,1,""],sendChangeNetworkRequest:[2,1,1,""],send_network_retrieval_request:[2,1,1,""],serveraddress:[2,2,1,""],serverport:[2,2,1,""],socket:[2,2,1,""]},"guicontroller.guicontroller":{HyperFlexHandler:[2,3,1,""],JsonRpcServer:[2,3,1,""]},"guicontroller.guicontroller.HyperFlexHandler":{get_all_vsdn:[2,1,1,""],get_physical_topo:[2,1,1,""],get_vsdn:[2,1,1,""],update_vsdn:[2,1,1,""]},"guicontroller.guicontroller.JsonRpcServer":{application:[2,1,1,""],start_server:[2,1,1,""]},"intelligence.guihandling":{ManagementGuiControllerHandler:[4,3,1,""]},"intelligence.guihandling.ManagementGuiControllerHandler":{get_all_vsdn_topos:[4,1,1,""],get_hypervisor_context:[4,1,1,""],get_physical_topo:[4,1,1,""],get_vsdn_topo:[4,1,1,""],process_network_change_request:[4,1,1,""]},"management.management":{sendToNetworkEmulator:[5,4,1,""]},data:{config:[1,0,0,"-"],dbinterfaces:[1,0,0,"-"],test:[1,0,0,"-"]},guicontroller:{config:[2,0,0,"-"],guiclient:[2,0,0,"-"],guicontroller:[2,0,0,"-"]},intelligence:{guihandling:[4,0,0,"-"]},management:{management:[5,0,0,"-"]},testcases:{start_json_receiver:[8,4,1,""],storm_test:[8,4,1,""],test_case_all_vsdn:[8,4,1,""],test_case_insert:[8,4,1,""],test_case_remove:[8,4,1,""],test_get_vsdn_topo:[8,4,1,""],test_network_retrieval:[8,4,1,""],test_physical_topo_retrieval:[8,4,1,""]}},objnames:{"0":["py","module","Python module"],"1":["py","method","Python method"],"2":["py","attribute","Python attribute"],"3":["py","class","Python class"],"4":["py","function","Python function"],"5":["py","data","Python data"]},objtypes:{"0":"py:module","1":"py:method","2":"py:attribute","3":"py:class","4":"py:function","5":"py:data"},terms:{"__del__":1,"__iter__":1,"__storm_table__":1,"_host":1,"_info":1,"boolean":1,"case":1,"class":[1,2,4],"default":1,"float":1,"function":8,"int":[1,2,4],"new":1,"return":[1,2,4],"switch":[1,2,4],"true":[1,2],abil:1,accompani:1,accordingli:1,action:[1,2],actual:1,add:[1,2],add_control:1,add_host:1,add_logical_edg:1,add_logical_link_embed:1,add_physical_edg:1,add_physical_port:1,add_physical_switch:1,add_serv:1,address:[1,2],admin:2,all:[1,2,4],alloc:[1,2,4],allow:2,along:1,alreadi:1,also:1,alter:2,ani:[1,2],anoth:1,applic:2,arg:2,argument:1,artifact:1,ascertionerror:1,assertionerror:[1,4],assertsionerror:1,assign:1,attribut:[1,4],backward:1,base:[1,2],behaviour:4,bein:1,belong:[1,2,4],between:[1,2],both:1,c_plane:1,can:1,canon:1,care:1,chang:[2,4],clean:1,client:2,code:1,color:1,column:1,com:[],come:1,command:1,commit:1,commun:2,compon:8,configur:1,connect:1,connector:1,conroller_id:1,consist:1,constant:2,contain:[1,2,4],context:1,control:[1,2],controller_id:1,convent:1,cool_switch:1,correct:1,cplane:[1,2],creat:1,cursiv:1,databas:[1,4],databs:1,default_switch_ip_port:1,default_switch_ip_prefix:1,defin:[1,2],delet:1,depend:1,descript:1,descriptor:1,design:1,destroi:1,detail:[1,2],develop:1,dictinari:1,dictionari:[1,2,4],differ:[2,8],directli:1,displai:1,doe:[1,2],down:1,dpid:[1,2],dure:1,dynamic_topolog:2,each:2,edg:[1,2,4],edge_id:1,either:1,element:4,embed:[1,4],embedding_id:1,end:1,endpoint:1,engin:1,entiti:2,entri:1,equival:1,error:[1,2],establish:1,even:1,event:4,everth:1,everti:1,everyth:1,exampl:[1,2],exist:1,explan:1,extend:1,fals:[1,2],fetch:1,file:2,first:1,flush:1,follow:2,fore:1,foreign:1,format:[1,2],from:[1,4],from_nod:[1,2],from_port:2,get:[1,4],get_all_vsdn:2,get_all_vsdn_topo:4,get_config:2,get_config_hyperflex_topo:1,get_config_hyperflex_topo_simpl:1,get_default_controller_port:1,get_edges_by_nod:1,get_host:1,get_hypervisor:1,get_hypervisor_context:4,get_link:1,get_network_nod:1,get_physical_topo:[1,2,4],get_switch:1,get_vsdn:[1,2],get_vsdn_topo:4,give:1,given:1,global:2,gui:[1,2,4],handl:[1,2,4],happen:1,hdic:4,hedg:1,henkel2:2,hex:1,high:1,host:[1,2,4],host_id:1,how:1,howev:1,html:[],http:[1,2],human:1,hyperflex_centr:2,hyperflexcor:2,hyperflexhandl:2,hyperflextopolog:1,hyperflextoposimpl:1,hyperflextoposimpleconnector:1,hypervisor:[1,2,4],hypervisor_id:1,identifi:[1,2,4],implement:[1,2,8],includ:2,index:3,info:1,info_class:1,info_typ:1,infoherit:1,infoheritance_desc:1,inform:1,infrastructur:2,inherit:1,init:2,initi:2,inlud:2,insert:1,instanc:1,instanci:1,integ:[1,4],interfac:1,intern:[1,2],ip_port:[1,2],ipv4:1,iter:1,itermixin:1,itself:4,json:2,jsonrpcserv:2,kalmbach:1,kei:[1,4],kwarg:1,label:[1,2],later:4,level:1,link:[1,2,4],list:[1,2,4],listen:[1,2],lkn:[1,2],load:1,locat:[1,2],logiacl:4,logic:[1,2,4],logical_edg:1,logical_edge_id:1,logicaledg:[1,4],logicaledgeembed:1,logocaledg:1,mac:1,made:4,mai:1,main:4,managementguicli:2,managementguicontrol:2,managementguicontrollerhandl:4,mani:1,manual:1,map:1,mapper:1,mask:1,mean:2,member:2,messag:[2,5],method:1,miss:1,moment:4,monospac:1,more:1,multipl:1,my_gui:1,my_guy_id:1,mygui:1,mysql:[],name:[1,2],narrow:1,neither:1,network:[1,2,4],network_nod:1,network_node_id:1,network_node_info_typ:1,networknod:1,networknodeinfo:1,newli:1,node:[1,2],node_id:1,node_on:1,node_one_id:1,node_two:1,node_two_id:1,none:[1,2,4],note:1,num_port:[1,2],number:1,numer:1,object:1,occur:2,occurr:1,on_remot:1,onli:1,onto:1,oper:4,option:[1,4],orchestr:4,order:1,orini:1,orm:1,other:[1,4],other_gui:1,other_guy_id:1,othergui:1,over:1,overwrit:1,page:3,pair:1,paramet:[1,2,4],parent:1,part:1,pass:1,path:1,pattern:1,perform:[1,2],persist:4,physic:[1,2,4],physical_edge_id:1,physical_embed:1,physicaledg:1,physicalport:1,physicalswitch:1,plane:1,point:[1,4],port1:1,port2:1,port:[1,2],port_id:1,port_on:1,port_one_id:1,port_two:1,port_two_id:1,present:4,primari:[1,4],print:1,process:4,process_network_change_request:4,programmat:1,properti:1,provid:1,purpos:1,push:1,put_link:1,put_network_nod:1,put_switch:1,put_vsdn:1,python:1,queri:1,rade:2,radix:[],rais:[1,4],rate:1,rather:1,rdbm:1,readabl:1,real:1,realiz:1,record:1,ref:1,refer:1,referenc:1,references_and_subclass:[],regist:1,register_network_node_info_typ:1,reign:1,relat:[1,4],relationship:1,remov:[1,2],remove_control:1,remove_host:1,remove_link:1,remove_logical_edg:1,remove_logical_edge_embed:1,remove_network_nod:1,remove_physical_edg:1,remove_physical_port:1,remove_physical_switch:1,remove_serv:1,remove_switch:1,remove_switch_to_vsdn:1,remove_ten:1,remove_vsdn:1,repres:1,represent:1,request:[2,4],resolv:1,respect:1,respons:1,ressourc:[1,2],retriev:[1,2,4],retun:2,run:1,runtimeerror:1,schema:1,search:3,second:1,see:2,select:1,send:2,send_network_retrieval_request:2,sendchangenetworkrequest:2,sendtonetworkemul:5,separ:1,serial:2,serv:1,server:2,server_id:1,serveraddress:2,serverport:2,set:[1,2],should:[1,2],simpl:1,sinc:1,slice:1,socket:2,softwar:1,somestor:1,sourc:[1,2,4,5,8],specif:[1,2,4],specifi:1,speed:1,sql:1,start:[1,2,4],start_json_receiv:8,start_serv:2,statement:1,statisticsguicontrol:2,statu:1,store:1,storednetworknodeinfo:1,storm:1,storm_test:8,stormconnector:1,string:[1,2],strom:1,student:[1,2],stuff:1,subclass:1,subnet:1,superclass:1,switch_id:1,switchtovsdn:1,tak:4,take:1,task:1,tenant:[1,2,4],tenant_id:[1,4],termin:1,test_case_all_vsdn:8,test_case_insert:8,test_case_remov:8,test_get_vsdn_topo:8,test_network_retriev:8,test_physical_topo_retriev:8,testcas:[],thei:2,them:[1,2],therefor:1,thi:[1,4],though:1,through:4,time:1,to_dictionari:1,to_nod:[1,2],to_port:2,topolog:[1,2,4],transact:1,transit:1,tri:1,trigger:4,tum:[1,2],turn:1,tutori:1,twistedmatrix:[],type:[1,2,4],typic:1,unittest:8,updat:[1,2],update_vsdn:2,user:[2,4],user_id:2,user_typ:2,util:1,valu:1,variabl:2,variou:1,vsdn:[1,2,4],vsdn_id:[1,2,4],want:1,when:1,where:1,whether:1,which:1,whole:[2,4],whose:[1,2],wiki:[1,2],work:1,wrapper:1,write:[1,4],written:1,you:1,your:1},titles:["HyperFLEX Core API","data package","guicontroller package","Welcome to HyperFLEX Core&#8217;s documentation!","intelligence package","management package",".","test module","testcases module"],titleterms:{api:0,backend:5,config:[1,2],content:[1,2,4,5],core:[0,3],data:1,dbinterfac:1,document:3,guiclient:2,guicontrol:2,guihandl:4,hyperflex:[0,3],indic:3,intellig:4,manag:5,modul:[1,2,4,5,7,8],packag:[1,2,4,5],submodul:[1,2,4,5],tabl:3,test:[1,7],testcas:8,welcom:3}})