#include "python_executer.h"

#include <iostream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>

// <ProjectName> <FileToRun> <ProgramArguments>...
void PythonExecuter::execute(const std::vector<std::string>& args)
{
    // Build command
    std::stringstream command;
    command << "python3 ";
    size_t num_args = args.size();
    for(int i = 1; i < num_args; i++)
    {
        const std::string& argument = args[i];
        command << argument;
        if (i < num_args-1)
        {
            command << " ";
        }
    }

    // 'cd' into project directory
    std::stringstream directory;
    directory << "PythonProjects/" << args[0];
    chdir(directory.str().c_str());

    // Execute command
    system(command.str().c_str());
}