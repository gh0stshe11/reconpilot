"""Base classes for tool adapters"""
import asyncio
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Optional

from reconpilot.core.models import Asset, Finding


class ToolCategory(Enum):
    """Categories of reconnaissance tools"""
    DNS = "dns"
    SUBDOMAIN = "subdomain"
    PORT_SCAN = "port_scan"
    WEB_PROBE = "web_probe"
    VULNERABILITY = "vulnerability"
    OSINT = "osint"
    TECHNOLOGY = "technology"
    FUZZING = "fuzzing"


@dataclass
class ToolResult:
    """Result from a tool execution"""
    tool_name: str
    success: bool
    assets: list[Asset] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    raw_output: str = ""
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolConfig:
    """Configuration for a tool adapter"""
    name: str
    binary: str
    category: ToolCategory
    description: str
    timeout: int = 300
    requires_root: bool = False
    produces: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)


class ToolAdapter(ABC):
    """Abstract base class for tool adapters"""

    def __init__(self, config: ToolConfig):
        self.config = config
        self._process: Optional[asyncio.subprocess.Process] = None

    def is_available(self) -> bool:
        """Check if the tool binary is available"""
        return shutil.which(self.config.binary) is not None

    @abstractmethod
    def build_command(self, target: str, **kwargs) -> list[str]:
        """Build the command to execute"""
        pass

    @abstractmethod
    def parse_output(self, output: str) -> ToolResult:
        """Parse tool output into structured results"""
        pass

    def parse_partial(self, output: str) -> ToolResult:
        """Parse partial output for real-time updates"""
        # Default implementation - can be overridden
        return ToolResult(tool_name=self.config.name, success=False)

    async def execute(self, target: str, **kwargs) -> AsyncGenerator[ToolResult, None]:
        """Execute the tool and stream results"""
        if not self.is_available():
            yield ToolResult(
                tool_name=self.config.name,
                success=False,
                error=f"Tool binary '{self.config.binary}' not found",
            )
            return

        command = self.build_command(target, **kwargs)
        
        try:
            self._process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_data = []
            stderr_data = []

            # Read output
            while True:
                try:
                    line = await asyncio.wait_for(
                        self._process.stdout.readline(),
                        timeout=self.config.timeout
                    )
                    if not line:
                        break
                    
                    line_str = line.decode("utf-8", errors="ignore")
                    stdout_data.append(line_str)
                    
                    # Try to parse partial output
                    partial_result = self.parse_partial("".join(stdout_data))
                    if partial_result.success and (partial_result.assets or partial_result.findings):
                        yield partial_result

                except asyncio.TimeoutError:
                    if self._process:
                        self._process.kill()
                    yield ToolResult(
                        tool_name=self.config.name,
                        success=False,
                        error=f"Timeout after {self.config.timeout}s",
                    )
                    return

            # Read stderr
            stderr = await self._process.stderr.read()
            stderr_data.append(stderr.decode("utf-8", errors="ignore"))

            # Wait for process to complete
            await self._process.wait()

            # Parse final output
            full_output = "".join(stdout_data)
            result = self.parse_output(full_output)
            
            if self._process.returncode != 0 and not result.success:
                result.error = "".join(stderr_data)

            yield result

        except Exception as e:
            yield ToolResult(
                tool_name=self.config.name,
                success=False,
                error=str(e),
            )
        finally:
            if self._process:
                try:
                    self._process.kill()
                except Exception:
                    pass
                self._process = None

    async def cancel(self) -> None:
        """Cancel the running tool"""
        if self._process:
            try:
                self._process.kill()
                await self._process.wait()
            except Exception:
                pass
            finally:
                self._process = None
