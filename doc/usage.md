# Usage Instructions for Dell Qiskit Runtime Emulator

##### Note: This is not a tutorial for Qiskit; only the Dell Qiskit Runtime Emulator. Features of Qiskit are documented in the Qiskit Textbook and are not covered here. 

## Local Execution Setup

Presuming that the Dell Qiskit Runtime Emulator is installed on your working machine, all that is required to start the local runtime environment is the following:

* Import the `EmulatorProvider`:
<pre>from qiskit_emulator import EmulatorProvider</pre>

* Create the `EmulatorProvider` object:
  
<pre>provider = EmulatorProvider()</pre>

Through `provider`, you can now access both the `provider.runtime` methods and the available backends.

## Remote Execution Setup

To set up the remote execution environment, presuming that you already have a Dell Qiskit Runtime Emulator Server deployed on a Kubernetes cluster, first follow the local execution steps and then perform the following:

* Specify the remote connection through your `EmulatorProvider`:
<pre>provider.remote({server IP/URL})</pre>

The server IP/URL can be retrieved from an environment variable or hard-coded into your programs.

If you do not have SSO enabled, the server will return a user ID to you. If you wish to return to your uploaded programs to manage or run them again, you may save that user ID and export it as an environment variable (`$QRE_ID`). The `EmulatorProvider` will check for this and use it if it is available.

If you do have SSO enabled on your server, the usual SSO login process will initiate at this step. Provide your credentials to your identity provider and the server will log you in. If you have a valid token from your identity provider, you may export that as an environment variable (`$TOKEN`) and the provider will use that to authenticate you.

## Program Upload

The interfaces provided by the local and remote runtime environments are identical, so the remaining sections apply to both.

To upload a program to the runtime environment, run:
<pre>
program_id =  provider.runtime.upload_program(                        \
              (required) {data},                                      \
              (optional) metadata={metadata},                         \
              (optional) name={name},                                 \
              (optional) max_execution_time={max_execution_time},     \
              (optional) description={description},                   \
              (optional) version={version},                           \
              (optional) backend_requirements={backend_requirements}, \
              (optional) parameters={parameters},                     \
              (optional) return_values={return_values},               \
              (optional) interim_results={interim_results},           \
          )
</pre>

The only required field is the `data` field. The parameter itself must be a string, but that string can represent the data in three different ways:
* String containing a full program, complete with `main` function.
* String containing a path to a file containing a full program.
* String containing a path to a directory of files.
  * One of these files in the top-level of that directory *must* be named `program.py` and contain `main`.

It is also worth noting that the `main` function implemented in any of these three options must take at least two required parameters:
* `backend`: The quantum backend on which your quantum code will run.
* `user_messenger`: The means by which your bundle will return results to your client-side code.

Other inputs can be named or put in `**kwargs`.

The `metadata` field takes a dictionary comprised of the remaining parameters in the `provider.runtime.upload_program` call. It is legal to provide either one metadata object or provide each field as a parameter to the function. 

None of the collected metadata affects the execution of the program itself, but it can be useful for maintaining information about which programs have been saved to the server and how they are called.

The `upload_program` function returns a program ID. This ID is the reference to the uploaded program on the server for any future operations you are able to perform with that program.

## Execution 

In the Qiskit Runtime, the term 'program' refers to the bundle of classical and quantum code that a user has uploaded. A 'job,' however is an instance of that program run with one set of inputs. 

To begin a job using the Dell Qiskit Runtime Emulator, run:
<pre>
job = provider.runtime.run(                                 \
                            (required) {program_id},        \
                            (required) options={options},   \
                            (required) inputs={inputs},     \
                            (optional) callback={callback}  \
                          )
</pre>

In the above call, the required parameters are the program ID (provided from the runtime in the previous step), the options (can be `None`), and the inputs. The `options` and the `inputs` are both dictionaries, where `options` determine how a program is run and `inputs` are provided to the uploaded client code's `main` function.

Returned from this call is a `job` object, which allows the user to check on the status (`job.status()`) of the job as well as access any messages that have been sent back from the job.

### Obtaining Results

To obtain any intermediate results your uploaded bundle may output, you may use the following:

<pre>
int_results = job.get_unread_messages()
</pre>

The `get_unread_messages` function will return a list of all messages that have not yet been returned by previous `get_unread_messages` calls.

It is important to note that _results marked `final` are not returned from `get_unread_messages`_. To obtain the `final` results from your program's execution you must use:

<pre>
final_results = job.result()
</pre>

`result` called with no parameter will return either the final results of the job, if they have been received, or `None` if they have not.

Optionally, you may call `result` with a `timeout`, expressed in seconds.

<pre>
final_results = job.result(timeout=60)
</pre>

Be aware that if the call times out, an `Exception` will be raised.

## (Optional) Callback Function

When executing a program using the Dell Qiskit Runtime Emulator it may be helpful to process results as they are sent back. To do this, the interface provides two options: 
* Manually call `get_unread_messages` and perform whatever computations are necessary
* Provide a `callback` function to the `provider.runtime.run` call that is called upon each intermediate message's arrival

To provide a callback function to run for each intermediate message, you may provide a function name in the call to `provider.runtime.run`. The function specified can be a built-in function, a library function, or a user-defined function. The function must, however, take a dictionary representing the message as its only parameter:

<pre>
def custom_callback(*args):
  (nfev, parameters, energy, stddev) = args[0]
  intermediate_info['nfev'].append(nfev)
  intermediate_info['parameters'].append(parameters)
  intermediate_info['energy'].append(energy)
  intermediate_info['stddev'].append(stddev)

job = provider.runtime.run(program_id, options=options, inputs=inputs, callback=custom_callback)
</pre>

Upon the `job` object's receipt of intermediate messages, it will call the `custom_callback` and handle the data.

## (Optional) Backend Selection

The default backend provided by the Dell Qiskit Runtime Emulator is IBM's Qiskit Aer. However, there are other backends implemented. If you wish to run the quantum portions of your code on a QPU or simulator, you may provide this information in the `inputs` dictionary:

<pre>
inputs = {
  'backend_name' = '{name_of_quantum_backend}',
  'backend_token' = '{backend_access_token}'
}
</pre>

Some available backends require access tokens - if the backend you've selected does, you must provide it in `inputs`. If the backend you've chosen does not require a token, you may omit this field.

If the backend you've selected is available in the listing provided by the Dell Qiskit Runtime Emulator Server, it will be used to run the quantum portions of your code.

If the backend is not available, IBM's Qiskit Aer will be used instead.


