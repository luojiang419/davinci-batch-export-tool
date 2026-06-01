"""
批量导出引擎 - 遍历时间线、配置渲染参数、调用 Resolve API 执行导出
"""
import os
from typing import List, Dict, Callable, Optional

from ..utils.resolve_api import get_api, ResolveAPIError
from ..core.export_settings_model import ExportSettings
from ..core.naming_engine import get_naming_engine


class ExportJob:
    """单个导出任务"""

    def __init__(self, timeline_name: str, output_filename: str,
                 output_path: str, folder: str = ""):
        self.timeline_name = timeline_name
        self.output_filename = output_filename
        self.output_path = output_path
        self.folder = folder
        self.job_id: Optional[str] = None
        self.status: str = "pending"  # pending / queued / rendering / done / failed
        self.error_message: str = ""

    @property
    def full_path(self) -> str:
        return os.path.join(self.output_path, self.output_filename)


class ExportEngine:
    """批量导出引擎"""

    def __init__(self):
        self._api = get_api()
        self._naming = get_naming_engine()
        self._jobs: List[ExportJob] = []
        self._is_running: bool = False
        self._progress_callback: Optional[Callable] = None
        self._log_callback: Optional[Callable] = None

    # ── 公共接口 ──────────────────────────────────────

    def create_jobs(self, selected_timelines: List[dict],
                    settings: ExportSettings) -> List[ExportJob]:
        """
        为每条选中的时间线创建导出任务

        Args:
            selected_timelines: [{"name", "duration", "fps", "folder"}, ...]
            settings: 导出设置

        Returns:
            创建的 ExportJob 列表
        """
        self._jobs = []
        self._naming.reset_counter()

        ext = settings.file_extension

        for i, tl_data in enumerate(selected_timelines):
            name = tl_data["name"]
            fps = tl_data.get("fps", "24")

            # 生成文件名
            base_name = self._naming.generate_filename(
                settings.naming_template,
                timeline_name=name,
                index=i + 1,
                project=self._api.get_project_name(),
                resolution=f"{settings.width}x{settings.height}",
                fps=fps,
                format=settings.format,
                codec=settings.video_codec,
            )
            filename = f"{base_name}{ext}"

            job = ExportJob(
                timeline_name=name,
                output_filename=filename,
                output_path=settings.output_path,
                folder=tl_data.get("folder", ""),
            )
            self._jobs.append(job)

        return self._jobs

    def execute(self, settings: ExportSettings,
                progress_callback: Callable = None,
                log_callback: Callable = None) -> bool:
        """
        执行批量导出

        Args:
            settings: 导出设置
            progress_callback: 进度回调 (current, total, job_name)
            log_callback: 日志回调 (message)

        Returns:
            是否全部成功
        """
        self._progress_callback = progress_callback
        self._log_callback = log_callback
        self._is_running = True

        if not self._jobs:
            self._log("没有待导出的任务")
            return False

        if self._api.is_mock:
            return self._execute_mock()

        return self._execute_real(settings)

    def cancel(self):
        """取消导出"""
        self._is_running = False
        if not self._api.is_mock:
            self._api.delete_all_render_jobs()

    def get_status(self) -> dict:
        """获取当前状态"""
        total = len(self._jobs)
        completed = sum(1 for j in self._jobs if j.status == "done")
        failed = sum(1 for j in self._jobs if j.status == "failed")
        running = sum(1 for j in self._jobs if j.status == "rendering")
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": total - completed - failed - running,
            "is_running": self._is_running,
        }

    # ── 实际导出 ──────────────────────────────────────

    def _execute_real(self, settings: ExportSettings) -> bool:
        """在真实 Resolve 环境中执行导出"""
        try:
            project = self._api.get_current_project()
            render_settings = settings.to_resolve_render_settings()
            render_settings["TargetDir"] = settings.output_path

            # 确保输出目录存在
            os.makedirs(settings.output_path, exist_ok=True)

            job_ids = []
            for i, job in enumerate(self._jobs):
                if not self._is_running:
                    break

                self._report_progress(i + 1, len(self._jobs), job.timeline_name)
                self._log(f"添加渲染: {job.timeline_name} → {job.output_filename}")

                # 切换到目标时间线
                timeline = self._find_timeline_by_name(job.timeline_name)
                if timeline is None:
                    job.status = "failed"
                    job.error_message = f"未找到时间线: {job.timeline_name}"
                    self._log(f"错误: {job.error_message}")
                    continue

                project.SetCurrentTimeline(timeline)

                # 配置渲染名称
                render_settings["CustomName"] = os.path.splitext(
                    job.output_filename
                )[0]

                # 应用渲染设置
                project.SetRenderSettings(render_settings)

                # 添加到渲染队列
                try:
                    job_id = project.AddRenderJob()
                    job.job_id = job_id
                    job.status = "queued"
                    job_ids.append(job_id)
                except Exception as e:
                    job.status = "failed"
                    job.error_message = str(e)
                    self._log(f"添加渲染失败: {e}")

            if not job_ids:
                self._log("没有成功添加到渲染队列的任务")
                return False

            # 开始渲染
            self._log(f"开始渲染 {len(job_ids)} 个任务...")
            project.StartRendering(*job_ids)

            # 等待渲染完成
            for job in self._jobs:
                if job.job_id and job.status == "queued":
                    job.status = "rendering"
                    try:
                        status = project.GetRenderJobStatus(job.job_id)
                        if status == "Complete":
                            job.status = "done"
                        else:
                            job.status = "failed"
                            job.error_message = f"状态: {status}"
                    except Exception as e:
                        job.status = "failed"
                        job.error_message = str(e)

            self._is_running = False
            status = self.get_status()
            self._log(f"导出完成: {status['completed']} 成功, "
                      f"{status['failed']} 失败")
            return status["failed"] == 0

        except Exception as e:
            self._log(f"导出过程出错: {e}")
            self._is_running = False
            return False

    def _execute_mock(self) -> bool:
        """Mock 模式模拟导出"""
        import time

        self._log(f"Mock模式: 模拟导出 {len(self._jobs)} 个任务...")

        for i, job in enumerate(self._jobs):
            if not self._is_running:
                break
            self._report_progress(i + 1, len(self._jobs), job.timeline_name)
            self._log(f"导出: {job.timeline_name} → {job.output_filename}")

            # 模拟渲染时间
            time.sleep(0.3)

            job.status = "done"

        self._is_running = False
        self._log(f"Mock导出完成: 全部 {len(self._jobs)} 个任务成功")
        return True

    def _find_timeline_by_name(self, name: str):
        """按名称查找时间线对象"""
        count = self._api.get_timeline_count()
        for i in range(1, count + 1):
            tl = self._api.get_timeline_by_index(i)
            if tl.GetName() == name:
                return tl
        return None

    def _report_progress(self, current: int, total: int, name: str):
        if self._progress_callback:
            self._progress_callback(current, total, name)

    def _log(self, message: str):
        if self._log_callback:
            self._log_callback(message)
