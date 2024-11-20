/**
 * shell
 * CS 341 - Spring 2024
 */
#include "format.h"
#include "shell.h"
#include "includes/vector.h"
#include "includes/sstring.h"
#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>
#include <dirent.h>
#include <sys/sysinfo.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#define STATUS_RUNNING "Running"
#define STATUS_STOPPED "Stopped"

//do not store exit command in history

typedef struct process {
    char *command;
    pid_t pid;
    char *status;
} process;
  
static FILE *source = NULL;
static vector *history = NULL;
static char *history_file_name = NULL;
static vector* processes = NULL;


size_t set_proccess_status(pid_t pid, char* status) {
    for (size_t i = 0; i < vector_size(processes); ++i) {
        process *p = vector_get(processes, i);
        if (p->pid == pid) {
            p->status = status;
            return i;
        }
    }
    return -1;
}

void signal_handler(int signal) {
    // if (signal == SIGINT) {
        // capture SIGINT, and do nothing
    // } else if (signal == SIGCHLD) {
    //     pid_t pid = 0;
    //     int status = 0;
    //     if ((pid = waitpid(-1, &status, WNOHANG)) != -1) {
    //         set_proccess_status(pid, "Killed");
    //     }
    // 
}



void add_process(char *command, char *status, pid_t pid) {
    for (size_t i = 0; i < vector_size(processes); ++i) {
        process *p = vector_get(processes, i);
        if (p->pid == pid) {
            p->command = command;
            p->status = status;
            return;
        }
    }
    process *p = malloc(sizeof(process));
    p->command = command;
    p->status = status;
    p->pid = pid;
    vector_push_back(processes, p);
}



void shell_exit(int status) {
    for (size_t i = 1; i < vector_size(processes); ++i) {
        process *p = vector_get(processes, i);
        if (strcmp(p->status, "Killed") && getpgid(p->pid) != p->pid) {
            kill(p->pid, SIGKILL);
        }
    }
    if (history_file_name != NULL) {
        FILE *history_file = fopen(history_file_name, "w");
        for (size_t i = 0; i < vector_size(history); ++i) {
            fprintf(history_file, "%s\n", (char*)vector_get(history, i));
        }
        fclose(history_file);
    }
    vector_destroy(history);
    if (source != stdin) {
        fclose(source);
    }
    exit(status);
}

 

void read_input(int argc, char *argv[]) {
    int opt;
    FILE* file = NULL;
    char* line = NULL;
    size_t len = 0;
    while ((opt = getopt(argc, argv, "h:f:")) != -1) {
        switch(opt) {
            case 'h':
                file = fopen(optarg, "r");
                if (file == NULL) {
                    file = fopen(optarg, "w");
                    if (file == NULL) {
                        print_history_file_error();
                        shell_exit(1);
                    }
                    fclose(file);
                    file = fopen(optarg, "r");
                }
                if (file == NULL) {
                    print_history_file_error();
                    shell_exit(1);
                }
                while (getline(&line, &len, file) != -1) {
                    if (line[strlen(line) - 1] == '\n') {
                        line[strlen(line) - 1] = '\0';
                    }
                    vector_push_back(history, line);
                }
                free(line);
                line = NULL;
                fclose(file);
                history_file_name = get_full_path(optarg);
                break;
            case 'f':
                file = fopen(optarg, "r");
                if (file == NULL) {
                    print_script_file_error();
                    shell_exit(1);
                }
                source = file;
                break;
            case '?':
                print_usage();
                shell_exit(1);
            default:
                break;
        }
    }
}

//wrtie a function that takes a string in char* and then checks if the string enfs with an & and if it does then remove the and and the trainiling white space 
//and return 1 else return 0
int isBackground(char* cmd) {
    size_t len = strlen(cmd);

    // Check if the last argument is "&"
    if (len > 0 && cmd[len - 1] == '&') {
        // Remove the "&" and any subsequent whitespace
        while (len > 0 && (cmd[len - 1] == ' ' || cmd[len - 1] == '&')) {
            cmd[--len] = '\0';
        }

        return 1;
    }

    return 0;
}

static vector* get_process_info() {
    vector* result = shallow_vector_create();

    struct sysinfo s_info;
    sysinfo(&s_info);
    time_t boot_time = time(NULL) - s_info.uptime;
    for (size_t i = 0; i < vector_size(processes); i++) {
        process* p = (process*)vector_get(processes, i);
        process_info* pinfo = (process_info*)malloc(sizeof(process_info));
        pinfo->pid = p->pid;
        char path[256];
        char line[256];
        FILE *file;
        pinfo->pid = p->pid;
        pinfo->command = strdup(p->command);
        sprintf(path, "/proc/%d/status", p->pid);
        file = fopen(path, "r");
        if (file) {
            while (fgets(line, sizeof(line), file)) {
                if (strncmp(line, "Threads:", 8) == 0) {
                    sscanf(line, "Threads: %ld", &pinfo->nthreads);
                    break;
                }
            }
            fclose(file);
        }

        sprintf(path, "/proc/%d/stat", p->pid);
        file = fopen(path, "r");
        if (file) {
            unsigned long utime, stime, vsize;
            unsigned long long starttime;
            fscanf(file, "%*d (%*[^)]) %c %*d %*d %*d %*d %*d %*u %*lu %*lu %*lu %*lu %lu %lu %*ld %*ld %*ld %*ld %*ld %*ld %llu %lu", &pinfo->state, &utime, &stime, &starttime, &vsize);
            fclose(file);
            pinfo->vsize = vsize / 1024;
            time_t start_time = (starttime / sysconf(_SC_CLK_TCK)) + boot_time;
            struct tm *tm_info = localtime(&start_time);
            pinfo->start_str = (char*)malloc(6);
            time_struct_to_string(pinfo->start_str, 6, tm_info);

            double total_time = (utime + stime) / (double)sysconf(_SC_CLK_TCK);
            size_t minutes = total_time / 60;
            size_t seconds = (size_t)total_time % 60;
            pinfo->time_str = (char*)malloc(10);
            execution_time_to_string(pinfo->time_str, 10, minutes, seconds);
        }
        //fclose(file);
        vector_push_back(result, pinfo);
    }
    return result;
}

int execute_single_command(const char* cmd, int want_to_push_to_history) {
    char* cpy_cmd = strdup(cmd);
    int background = isBackground(cpy_cmd);
    if (want_to_push_to_history) {
        vector_push_back(history, strdup(cmd)); 

    }
    if (strcmp(cmd, "exit") == 0) {
        shell_exit(0);
    } else if (strncmp(cmd, "cd ", 3) == 0) {
        const char* dir_path = cmd + 3;
        if (chdir(dir_path) != 0) {
            print_no_directory(dir_path);
            return 1;  // Indicate failure
        }
    } else if (strcmp(cmd, "ps") == 0) {
        print_process_info_header();
        process_info *info = NULL;
        vector* process_infos = get_process_info();

        for (size_t i = 0; i < vector_size(processes); ++i) {
            info = vector_get(process_infos, i);

            print_process_info(info);
        }
    } else {
        pid_t pid = fork();
        if (pid < 0) {
            print_fork_failed();
            shell_exit(1);
            return 1;  // Indicate failure
        } else if (pid == 0) {
            // In child process
            sstring* split_me = cstr_to_sstring(cpy_cmd);
            vector* external_commands = sstring_split(split_me, ' ');
            char** argv = malloc((vector_size(external_commands) + 1) * sizeof(char*));
            for (size_t i = 0; i < vector_size(external_commands); ++i) {
                argv[i] = vector_get(external_commands, i);
            }
            argv[vector_size(external_commands)] = NULL;
            execvp(argv[0], argv);

            print_exec_failed(cpy_cmd);
            for (size_t i = 0; i < vector_size(external_commands); ++i) {
                free(argv[i]);
            }
            free(argv);  // Only reached if execvp fails
            shell_exit(EXIT_FAILURE);  // Ensure the child process exits if exec fails
        } else {
            // In parent process
            int status;
            print_command_executed(pid);
            if (background) {
                add_process(strdup(cpy_cmd), "RUNNING", pid);
            } else {
                waitpid(pid, &status, 0);  // Wait for child process to finish
                if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                    // Success, command executed correctly
                } else {
                    print_wait_failed();
                    return 1; 
                }
            }
            
        }
    }
    return 0;  // Indicate success
}


void handle_redirection(const char* cmd, const char* file_name, const char* operator) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("Fork error");
        return;
    } else if (pid == 0) {
        int fd = 0;
        if (strcmp(operator, ">") == 0) {
            fd = open(file_name, O_CREAT | O_WRONLY | O_TRUNC, 0644);
            if (fd < 0) {
                print_redirection_file_error();
                shell_exit(1); // Terminate child process
            }
            dup2(fd, STDOUT_FILENO);
        } else if (strcmp(operator, ">>") == 0) {
            fd = open(file_name, O_CREAT | O_WRONLY | O_APPEND, 0644);
            if (fd < 0) {
                // Handle error
                print_redirection_file_error();
                shell_exit(1); // Terminate child process
            }
            dup2(fd, STDOUT_FILENO);
        } else if (strcmp(operator, "<") == 0) {
            fd = open(file_name, O_RDONLY);
            if (fd < 0) {
                // Handle error
                print_redirection_file_error();
                shell_exit(1); // Terminate child process
            }
            dup2(fd, STDIN_FILENO);
        }
        execlp("/bin/sh", "sh", "-c", cmd, (char *)0);
        close(fd);
        shell_exit(0); // Terminate child process
    } else {
        print_command_executed(pid);
        waitpid(pid, NULL, 0);
    }
}

void process_command(const char *cmd) {
    // char* copy_cmd = strdup(cmd);
    // if (isBackground(&copy_cmd) == 0) {
    //     printf("Baground process\n");
    // } 
    if (strcmp(cmd, "exit") == 0) {
        shell_exit(0);
    } else if (strcmp(cmd, "!history") == 0) {
        for (size_t i = 0; i < vector_size(history); i++) {
            print_history_line(i, vector_get(history, i));
        }
    } else if (cmd[0] == '!') {
        const char* prefix = cmd + 1;
        int boolean = 0;
        //printf("\n I am getting here and this is what i am trying to run");
        for (ssize_t i = vector_size(history) - 1; i >= 0; i--) {
            char* temp = (char*)vector_get(history, i);

             if (strncmp(temp, prefix, strlen(prefix)) == 0) {
                temp = strdup(temp);
                //vector_push_back(history, temp);
                print_command(temp);
                execute_single_command(temp, 1);
                free(temp);
                boolean = 1;
                break;
            }
        }
        if (boolean == 0) {
            print_no_history_match();
        }
    } else if (cmd[0] == '#') {
        const char* index = cmd + 1;
        if (atoi(index) >= (int)vector_size(history)) {
            print_invalid_index();
        } else {
            
            char* temp_cmd = vector_get(history, atoi(index));
            print_command(temp_cmd);
            //vector_push_back(history, temp_cmd);
            execute_single_command(temp_cmd, 1);
        }
    } else if (strstr(cmd, "&&") != NULL) {
        //sstring* split_me = cstr_to_sstring(cmd);
        vector_push_back(history, (void*)cmd);
        vector* logical_operator_split = string_vector_create();
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, "&&");

        while (token != NULL) {
            while (*token && isspace(*token)) {
                ++token;
            }
            char* end = token + strlen(token) - 1;
            while (end > token && isspace(*end)) {
                --end;
            }
            *(end + 1) = '\0';
            if (*token) {
                vector_push_back(logical_operator_split, token);
            }
            token = strtok(NULL, "&&");
        }

        for (size_t i = 0; i < vector_size(logical_operator_split); i++) {
            char* cmd_sstring = vector_get(logical_operator_split, i);
            int success = execute_single_command(cmd_sstring, 0);
            if (success == 1) {
                break;
            }
        }
    } else if (strstr(cmd, "||")) {
        vector_push_back(history, (void*)cmd);
        vector* logical_operator_split = string_vector_create();
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, "||");

        while (token != NULL) {
            while (*token && isspace(*token)) {
                ++token;
            }
            char* end = token + strlen(token) - 1;
            while (end > token && isspace(*end)) {
                --end;
            }
            *(end + 1) = '\0';
            if (*token) {
                vector_push_back(logical_operator_split, token);
            }
            token = strtok(NULL, "||");
        }

        for (size_t i = 0; i < vector_size(logical_operator_split); i++) {
            char* cmd_sstring = vector_get(logical_operator_split, i);
            int success = execute_single_command(cmd_sstring, 0);
            if (success == 0) {
                break;
            }
        }

    } else if (strstr(cmd, ";")) {
        vector_push_back(history, (void*)cmd);
        vector* logical_operator_split = string_vector_create();
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, ";");

        while (token != NULL) {
            while (*token && isspace(*token)) {
                ++token;
            }
            char* end = token + strlen(token) - 1;
            while (end > token && isspace(*end)) {
                --end;
            }
            *(end + 1) = '\0';
            if (*token) {
                vector_push_back(logical_operator_split, token);
            }
            token = strtok(NULL, ";");
        }
        for (size_t i = 0; i < vector_size(logical_operator_split); i++) {
            char* cmd_sstring = vector_get(logical_operator_split, i);
            execute_single_command(cmd_sstring, 0);
        }

    } else if (strstr(cmd, ">>") != NULL) {
        vector_push_back(history, (void*)cmd);
        vector* redirection_op_split = string_vector_create();
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, ">>");

        while (token != NULL) {
            while (*token && isspace(*token)) {
                ++token;
            }
            char* end = token + strlen(token) - 1;
            while (end > token && isspace(*end)) {
                --end;
            }
            *(end + 1) = '\0';
            if (*token) {
                vector_push_back(redirection_op_split, token);
            }
            token = strtok(NULL, ">>");
        }
        handle_redirection(vector_get(redirection_op_split, 0), vector_get(redirection_op_split, 1), ">>");


    } else if (strstr(cmd, ">") != NULL) {
        vector_push_back(history, (void*)cmd);
        vector* redirection_op_split = string_vector_create();
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, ">");

        while (token != NULL) {
            while (*token && isspace(*token)) {
                ++token;
            }
            char* end = token + strlen(token) - 1;
            while (end > token && isspace(*end)) {
                --end;
            }
            *(end + 1) = '\0';
            if (*token) {
                vector_push_back(redirection_op_split, token);
            }
            token = strtok(NULL, ">");
        }
        handle_redirection(vector_get(redirection_op_split, 0), vector_get(redirection_op_split, 1), ">");
    } else if (strstr(cmd, "<") != NULL) {
        vector_push_back(history, (void*)cmd);
        vector* redirection_op_split = string_vector_create();
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, "<");

        while (token != NULL) {
            while (*token && isspace(*token)) {
                ++token;
            }
            char* end = token + strlen(token) - 1;
            while (end > token && isspace(*end)) {
                --end;
            }
            *(end + 1) = '\0';
            if (*token) {
                vector_push_back(redirection_op_split, token);
            }
            token = strtok(NULL, "<");
        }
        handle_redirection(vector_get(redirection_op_split, 0), vector_get(redirection_op_split, 1), "<");
    } else if (strstr(cmd, "kill")  != NULL) {
        //my kill will look like kill <pid>, i want to parse the pid and send the signal to the process
        char* inputs[2];
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, " ");
        int i = 0;
        while (token != NULL) {
            inputs[i] = token;
            i++;
            token = strtok(NULL, " ");
        }
        pid_t target_pid = atoi(inputs[1]);
        size_t idx;
        if ((idx = set_proccess_status(target_pid, "Killed")) == (size_t)-1) {
            print_no_process_found(target_pid);
        }
        kill(target_pid, SIGKILL);
        print_killed_process(target_pid, ((process*)vector_get(processes, idx))->command);
    } else if (strstr(cmd, "stop") != NULL) {
        char* inputs[2];
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, " ");
        int i = 0;
        while (token != NULL) {
            inputs[i] = token;
            i++;
            token = strtok(NULL, " ");
        }
        pid_t target_pid = atoi(inputs[1]);
        size_t idx;
        if ((idx = set_proccess_status(target_pid, STATUS_STOPPED)) == (size_t)-1) {
            print_no_process_found(target_pid);
        }
        kill(target_pid, SIGSTOP);
        print_stopped_process(target_pid, ((process*)vector_get(processes, idx))->command);
    } else if (strstr(cmd, "cont") != NULL) {
        char* inputs[2];
        char* token;
        char* split = strdup(cmd);
        token = strtok(split, " ");
        int i = 0;
        while (token != NULL) {
            inputs[i] = token;
            i++;
            token = strtok(NULL, " ");
        }
        pid_t target_pid = atoi(inputs[1]);
        size_t idx;
        if ((idx = set_proccess_status(target_pid, STATUS_RUNNING)) == (size_t)-1) {
            print_no_process_found(target_pid);
        }
        kill(target_pid, SIGCONT);
    }
    else {
        execute_single_command(cmd, 1);
    }
   
}


void write_to_history_file(const char *file_path, const char *cmd) {
    FILE *file = fopen(file_path, "a");
    if (file != NULL) {
        fprintf(file, "%s\n", cmd);
        fclose(file);
    } else {
        fprintf(stderr, "Error opening history file: %s\n", file_path);
    }
}




int shell(int argc, char *argv[]) {
    signal(SIGINT, signal_handler);
    history = string_vector_create();
    processes = shallow_vector_create();
    source = stdin;
    read_input(argc, argv);

    process *for_shell = malloc(sizeof(process));
    if (for_shell == NULL) {
        // Handle allocation failure
        shell_exit(1);
    }
    for_shell->pid = getpid();
    for_shell->command = strdup("./shell");
    for_shell->status = strdup("Running");

    vector_push_back(processes, for_shell);



    char cwd[1024];
    if (source == stdin) {
       
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            print_prompt(cwd, getpid());
        } else {
            shell_exit(1);
        }
    }
    

    char* cmd = NULL;
    size_t size = 0;
    while (getline(&cmd, &size, source) != -1) {
        pid_t wpid;
        int status;
        //reaping zombies
        while ((wpid = waitpid(-1, &status, WNOHANG)) > 0) {
            size_t i = 0;
            for (; i < vector_size(processes); i++) {
                process* p = (process*)vector_get(processes, i);
                if (p->pid == wpid) {
                    free(p->command);
                    free(p);
                    vector_erase(processes, i);
                    break;
                }
            }
        }
        if (cmd[strlen(cmd) -1] == '\n') {
            cmd[strlen(cmd) - 1] = '\0';
        }
        char* temp = strdup(cmd);
        if (source == stdin) {
            process_command(temp);
            free(temp);
        }
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            print_prompt(cwd, getpid());
            if (source != stdin) {
                printf("%s\n", cmd);
            }
            fflush(stdout);
        } else {
            shell_exit(1);
        }

        if (source != stdin) {
            process_command(temp);
            free(temp);
        }
        
    }
    return 0;
}
