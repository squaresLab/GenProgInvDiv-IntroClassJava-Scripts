import com.github.javaparser.*;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.body.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class SeparateTests
{
	private static final String POS_TEST_SHORT_CLASS_NAME = "PositiveTest";
	private static final String NEG_TEST_SHORT_CLASS_NAME = "NegativeTest";

	/**
	 * @param path Path to pos.tests or neg.tests (a list of tests)
	 * @return a map mapping (full) classes -> methods
	 */
	private static Map<String, List<String>> getTestsMap(String path)
	{
		Map<String, List<String>> testMap = new HashMap<>(); //maps a class to positive test cases in the class
		List<String> testsRaw;
		try
		{
			testsRaw = Files.readAllLines(Paths.get(path));
		} catch (IOException e) {
			throw new IllegalArgumentException(e);
		}

		for(String t : testsRaw)
		{
			String[] parts = t.split("::");
			if(parts.length != 2)
				throw new IllegalArgumentException("Bad test in " + path + ": " + t);
			String clazz = parts[0];
			String method = parts[1];
			if(testMap.containsKey(clazz))
				testMap.get(clazz).add(method);
			else
			{
				List<String> methodsList = new ArrayList<>();
				methodsList.add(method);
				testMap.put(clazz, methodsList);
			}
		}
		return testMap;
	}

	/**
	 * @param clazz a class name in string form
	 * @return the package name of the class
	 */
	private static String getPackageNameFromClassName(String clazz)
	{
		String[] parts = clazz.split("\\.");
		StringBuilder packageName = new StringBuilder();
		for(int i = 0; i < parts.length - 1; i++)
			packageName.append(parts[i]);
		return packageName.toString();
	}

	/**
	 * @param a
	 * @param b
	 * @return a union b
	 */
	private static List<String> union(Set<String> a, Set<String> b)
	{
		List<String> u = new ArrayList<>(a);
		for(String s : b)
		{
			if(!u.contains(s))
				u.add(s);
		}
		return u;
	}

	private static CompilationUnit getCUOfExistingClass(String pathTestClasses, String fullClassName)
	{
		String classDotsReplaced = fullClassName.replace('.', File.separatorChar);
		String pathToClass = pathTestClasses + "/" + classDotsReplaced + ".java";
		CompilationUnit cu;
		try
		{
			cu = JavaParser.parse(new File(pathToClass));
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		}
		return cu;
	}

	private static CompilationUnit[] getExistingCUs(String pathTestClasses, List<String> curTestClasses)
	{
		CompilationUnit[] cus = new CompilationUnit[curTestClasses.size()];
		for(int i = 0; i < cus.length; i++)
		{
			cus[i] = getCUOfExistingClass(pathTestClasses, curTestClasses.get(i));
		}
		return cus;
	}


	private static CompilationUnit setupNewTestClassCU(CompilationUnit exampleCU)
	{
		CompilationUnit newCU = new CompilationUnit();
		Optional<PackageDeclaration> packageDec = exampleCU.getPackageDeclaration();
		if(packageDec.isPresent())
			newCU.setPackageDeclaration(packageDec.get());
		NodeList<ImportDeclaration> imports = exampleCU.getImports();
		if(imports != null)
			newCU.setImports(imports);
		return newCU;
	}

	private static String getShortClassName(String longClassName)
	{
		String[] parts = longClassName.split("\\.");
		return parts[parts.length - 1];
	}

	private static ClassOrInterfaceDeclaration getClassFromCUs(CompilationUnit[] cus, String shortClassName)
	{
		for(CompilationUnit cu : cus)
		{
			Optional<ClassOrInterfaceDeclaration> cand = cu.getClassByName(shortClassName);
			if(cand.isPresent())
				return cand.get();
		}
		return null;
	}

	private static List<MethodDeclaration> getMethodsFromClass(ClassOrInterfaceDeclaration sourceClass, List<String> methodsToGet)
	{
		List<MethodDeclaration> methodDecs = new ArrayList<>(methodsToGet.size());
		NodeList<BodyDeclaration<?>> membersOfSourceClass = sourceClass.getMembers();
		for(BodyDeclaration<?> member : membersOfSourceClass)
		{
			if(member instanceof MethodDeclaration)
			{
				MethodDeclaration md = (MethodDeclaration) member;
				if(methodsToGet.contains(md.getNameAsString()))
				{
					MethodDeclaration mdClone = md.clone();
					//change names to disambiguate different classes w/ same method names
					mdClone.setName(sourceClass.getNameAsString() + "_" + mdClone.getNameAsString());
					methodDecs.add(mdClone);
				}
			}
		}
		return methodDecs;
	}

	private static void addMethodsToClass(List<MethodDeclaration> methods, ClassOrInterfaceDeclaration destClass)
	{
		for(MethodDeclaration m : methods)
			destClass.addMember(m);
	}

	private static void copyTests(Map<String, List<String>> testsMap, CompilationUnit[] sourceCUs, ClassOrInterfaceDeclaration destClass)
	{
		for(String longClassName : testsMap.keySet())
		{
			String shortClassName = getShortClassName(longClassName);
			ClassOrInterfaceDeclaration sourceClass = getClassFromCUs(sourceCUs, shortClassName);
			if(sourceClass == null)
				throw new RuntimeException("Class not found in sourceCUs: " + longClassName);

			List<String> testMethodsToCopy = testsMap.get(longClassName);
			List<MethodDeclaration> methodDecs = getMethodsFromClass(sourceClass, testMethodsToCopy);
			addMethodsToClass(methodDecs, destClass);
		}
	}

	private static void writeCUToFile(CompilationUnit cu, String pathNewClasses, String packageName, String shortClassName)
	{
		String path = pathNewClasses + "/" + packageName.replace('.', File.separatorChar) + "/" +
				shortClassName + ".java";
		try
		{
			File f = new File(path);
			f.getParentFile().mkdirs();
			FileWriter fw = new FileWriter(f, false);
			String stuffToWrite = cu.toString();
			fw.write(stuffToWrite, 0, stuffToWrite.length());
			fw.close();
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

	private static void writeStringToFile(String data, String path)
	{
		try
		{
			File f = new File(path);
			//not making directories, file should already exist
			FileWriter fw = new FileWriter(f, false); //overwrite
			fw.write(data, 0, data.length());
			fw.close();
		}
		catch (IOException e)
		{
			throw new RuntimeException(e);
		}
	}

	private static String getFullClassName(String packageName, String shortClassName)
	{
		return packageName + "." + shortClassName;
	}

	private static void writeMethodsListToFile(String packageName, ClassOrInterfaceDeclaration classDec, String path)
	{
		String methods = "";
		for(BodyDeclaration<?> member : classDec.getMembers()) //don't use getMethodsFromClass, does different things
		{
			if(member instanceof MethodDeclaration)
			{
				MethodDeclaration md = (MethodDeclaration) member;
				methods += packageName + "." + classDec.getNameAsString() + "::" + md.getNameAsString() + "\n";
			}
		}

		try
		{
			File f = new File(path);
			//not making directories, file should already exist
			FileWriter fw = new FileWriter(f, false); //overwrite
			fw.write(methods, 0, methods.length());
			fw.close();
		}
		catch (IOException e)
		{
			throw new RuntimeException(e);
		}
	}

	public static void main(String[] args)
	{
		if(args.length != 4)
		{
			System.err.println("0th param: path to pos.tests (file will be overwritten)\n" +
					"1st param: path to neg.tests (file will be overwritten)\n" +
					"2nd param: path to directory to place new test classes in (must already exist)\n" +
					"3th param: path to the directory containing the currently existing test classes");
			System.exit(1);
		}

		String pathPosTests = args[0];
		String pathNegTests = args[1];
		String pathNewClasses = args[2];
		String pathTestClasses = args[3];

		Map<String, List<String>> posTestsMap = getTestsMap(pathPosTests);
		Map<String, List<String>> negTestsMap = getTestsMap(pathNegTests);
		List<String> curTestClasses = union(posTestsMap.keySet(), negTestsMap.keySet());
		CompilationUnit[] curCUs = getExistingCUs(pathTestClasses, curTestClasses);

		CompilationUnit posCU = setupNewTestClassCU(curCUs[0]);
		CompilationUnit negCU = setupNewTestClassCU(curCUs[0]);
		ClassOrInterfaceDeclaration posClassDec = posCU.addClass(POS_TEST_SHORT_CLASS_NAME);
		ClassOrInterfaceDeclaration negClassDec = negCU.addClass(NEG_TEST_SHORT_CLASS_NAME);
		copyTests(posTestsMap, curCUs, posClassDec);
		copyTests(negTestsMap, curCUs, negClassDec);

		String packageName = getPackageNameFromClassName(curTestClasses.get(0));
		//write new .java files
		writeCUToFile(posCU, pathNewClasses, packageName, POS_TEST_SHORT_CLASS_NAME);
		writeCUToFile(negCU, pathNewClasses, packageName, NEG_TEST_SHORT_CLASS_NAME);
		//overwrite pos.tests and neg.tests
		//writeStringToFile(getFullClassName(packageName, POS_TEST_SHORT_CLASS_NAME), pathPosTests);
		//writeStringToFile(getFullClassName(packageName, NEG_TEST_SHORT_CLASS_NAME), pathNegTests);
		writeMethodsListToFile(packageName, posClassDec, pathPosTests);
		writeMethodsListToFile(packageName, negClassDec, pathNegTests);

		//for daikon
		writeStringToFile(getFullClassName(packageName, POS_TEST_SHORT_CLASS_NAME), pathPosTests);
	}
}