import java.io.*;
import java.util.*;
import org.apache.commons.exec.*;
public class ServerAnalyzer{

public static void main(String[] args)throws IOException{

String productFile = args[0];
String downloadTarget = args[1];
String GP4JHOME = args[2];
List<String> listOfAres = new ArrayList<String>();
Scanner input = new Scanner(new File(productFile));

DefaultExecutor executor = new DefaultExecutor();
String workingDirectory = System.getProperty("user.dir");
executor.setWorkingDirectory(new File(workingDirectory));
executor.setExitValue(0);
ByteArrayOutputStream out = new ByteArrayOutputStream();
executor.setStreamHandler(new PumpStreamHandler(out));
int serial = 0;
while(input.hasNext()){
String[] splitted = input.nextLine().split(",");
for(int i = 0; i < 10; i++){
serial++;
CommandLine command = CommandLine.parse("aws s3 cp s3://gp4j-invdiv-short-results/"+splitted[0]+"_"+splitted[1]+"_"+splitted[2]+"_mode"+splitted[3]+"_ResultOfSeed"+i+".results "+downloadTarget);
System.out.println(command.toString());
try{
executor.execute(command);
}catch(ExecuteException e){
continue;
}
System.out.println("Done");

String no = out.toString();
out.flush();

command = CommandLine.parse("java -cp "+GP4JHOME+"/target/classes:"+GP4JHOME+"/lib/commons-lang3-3.8.1.jar ylyu1.wean.DataProcessor "+splitted[0]+" "+splitted[1]+" "+splitted[2]+" "+splitted[3]+" "+i+" "+downloadTarget);
executor.execute(command);

listOfAres.add(out.toString());

}
}

PrintWriter writer = new PrintWriter(new File("results.txt"));
for(String s : listOfAres){
writer.println(s);
}
writer.close();

}

}
