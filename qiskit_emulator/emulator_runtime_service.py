from typing import List, Dict, Optional, Callable, Type, Union, NamedTuple
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers import ProviderV1 as Provider

class ProgramParameter(NamedTuple):
    """Program parameter."""
    name: str
    description: str
    type: str
    required: bool


class ProgramResult(NamedTuple):
    """Program result."""
    name: str
    description: str
    type: str

class EmulatorRuntimeService():

    _programs = {}

    def __init__(self, provider: Provider) -> None:
        self.provider = provider


    def pprint_programs(self):
        return self._programs

    # copied from IBMQ Provider
    def pprint_programs(self, refresh: bool = False) -> None:
        """Pretty print information about available runtime programs.

        Args:
            refresh: If ``True``, re-query the server for the programs. Otherwise
                return the cached value.
        """
        programs = self.programs(refresh)
        for prog in programs:
            print("="*50)
            print(str(prog))

    def upload_program(
            self,
            data: Union[bytes, str],
            metadata: Optional[Union[Dict, str]] = None,
            name: Optional[str] = None,
            max_execution_time: Optional[int] = None,
            description: Optional[str] = None,
            version: Optional[float] = None,
            backend_requirements: Optional[str] = None,
            parameters: Optional[List[ProgramParameter]] = None,
            return_values: Optional[List[ProgramResult]] = None,
            interim_results: Optional[List[ProgramResult]] = None
    ) -> str:
        print("Do nothing")

    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        print("Do nothing")

    def programs(self, refresh: bool = False) -> List[RuntimeProgram]:
        return []

    def run(
            self,
            program_id: str,
            options: Dict,
            inputs: Dict,
            callback: Optional[Callable] = None,
            result_decoder: Optional[Type[ResultDecoder]] = None
    ) -> RuntimeJob:
        return None

    def delete_program(self, program_id: str) -> None:
        print("Do Nothing")

    def job(self, job_id: str) -> RuntimeJob:
        print("Do nothing")

    def jobs(self, limit: int = 10, skip: int = 0) -> List[RuntimeJob]:
        return []

    def delete_job(self, job_id: str) -> None:
        print("Do Nothing")

    def logout(self) -> None:
        print("Do Nothing")

    

    


