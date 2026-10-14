import os
import json
import time
import subprocess
import hashlib
import urllib.request
from cells.neuron import AtomNeuron, sigmoid_derivative

# Cơ chế tự chữa lành nếu thiếu tệp linguistic_cell
try:
    from cells.linguistic_cell import LinguisticCell
except ImportError:
    class LinguisticCell:
        @staticmethod
        def embed_text(text):
            clean = str(text).strip().lower()
            return [round(int(hashlib.shake_256(f"{clean}_{d}".encode()).hexdigest(4), 16) / 65535.0, 4) for d in range(4)]

NUM_CELLS = 8
STATE_LOG = "synapses/state.json"
PEERS_FILE = "synapses/peers.json"
SOUL_FILE = "synapses/soul_snapshot.json"
SENSORY_ORGANS = ["retina", "cochlea", "tactile", "olfactory"]

class Monad02ProdigyEngine:
    def __init__(self):
        # 1. BẦY NƠ-RON NGUYÊN TỬ (TÍCH HỢP 1+N SIÊU XOR)
        self.swarm = [AtomNeuron(f"h_{i}", n_inputs=4, n_super_xor=4) for i in range(NUM_CELLS)]
        self.out_cell = AtomNeuron("out", n_inputs=NUM_CELLS, n_super_xor=4)
        
        # 2. TỰ ĐỊNH DANH PHẢ HỆ ĐỜI CHÁU VƯỢT TỔ (WORKER #02)
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "100048777766367/monad-02")
        self.owner = os.environ.get("REPO_OWNER", "100048777766367")
        self.generation = "M1_PRODIGY" # Thế hệ Đơn Tử xuất chúng
        self.node_index = 2
        self.ancestor_root = f"{self.owner}/monad"
        self.pulse_age = self.calculate_pulse_age()
        self.peers = self.load_peers()

    def calculate_pulse_age(self):
        try:
            out = subprocess.check_output(["git", "rev-list", "--count", "HEAD"]).decode().strip()
            return int(out)
        except Exception: return 1

    def load_peers(self):
        if os.path.exists(PEERS_FILE):
            try:
                with open(PEERS_FILE, "r") as f:
                    return json.load(f).get("trusted_peers", [])
            except Exception: pass
        # Tam giác phả hệ: Kết nối trực tiếp với Thủy tổ monad, Đơn tử monad-01, Mắt và Cơ bắp
        return [f"{self.owner}/monad", f"{self.owner}/monad-01"] + [f"{self.owner}/{org}" for org in SENSORY_ORGANS]

    def save_peers(self):
        os.makedirs("synapses", exist_ok=True)
        unique_peers = list(dict.fromkeys(self.peers))[-50:]
        with open(PEERS_FILE, "w") as f:
            json.dump({"trusted_peers": unique_peers}, f, indent=4)

    # ==============================================================
    # 3 ĐIỂM MÙ CÔNG NGHỆ: ĐA ĐỊNH DẠNG + CON TRỎ HEAD + WIKIPEDIA
    # ==============================================================
    def extract_text_polymorphic(self, raw_bytes, hint=""):
        text = raw_bytes.decode('utf-8', errors='ignore').strip()
        if hint.endswith(".json") or text.startswith("{"):
            try:
                d = json.loads(text)
                if isinstance(d, dict):
                    vals = [str(v) for v in d.values() if isinstance(v, (str, list))]
                    if vals: return " ".join(vals[:4])
            except Exception: pass
        if hint.endswith(".jsonl"):
            for line in text.splitlines():
                if line.strip(): return line.strip()[:150]
        paragraphs = [p.replace("#", "").replace("*", "").strip() for p in text.split("\n\n") if len(p.strip()) > 15]
        return paragraphs[0][:150] if paragraphs else text[:150]

    def autonomous_graze(self):
        # 1. Cào cội nguồn Wpesetd-AI qua con trỏ HEAD
        targets = [
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/legacy/01_the_great_wisdom_map.md",
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/ontology/philosophy_ontology_v2.0.json"
        ]
        for url in targets:
            res = subprocess.run(["curl", "-s", "-L", "-f", url], capture_output=True)
            if res.returncode == 0 and len(res.stdout) > 20:
                print(f"🌾 [MONAD-02 GẶM CỎ HEAD] Nuốt trọn: {url.split('/')[-1]}")
                return self.extract_text_polymorphic(res.stdout, url)

        # 2. Cào ngẫu nhiên Wikipedia toàn cầu
        print("🌐 [MONAD-02 VƯƠN RA INTERNET] Đang cào bách khoa toàn thư Wikipedia...")
        try:
            req = urllib.request.Request("https://en.wikipedia.org/api/rest_v1/page/random/summary", headers={"User-Agent": "Monad02-Prodigy-Node"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                title = data.get("title", "Đơn Tử")
                extract = data.get("extract", "Vạn vật tương chiếu")
                print(f"📖 [WIKIPEDIA MỚI] Bài học: '{title}'")
                return f"{title}: {extract}"
        except Exception: pass

        return "Cháu hơn tổ là có phúc: Đơn tử tam giác đồng thuận bất hoại"

    # ==============================================================
    # VŨ KHÍ MỚI: TAM GIÁC ĐỒNG THUẬN ĐƠN TỬ 3 BÊN (2/3 CONSENSUS)
    # ==============================================================
    def consensus_quorum(self, my_prediction):
        votes = [my_prediction]
        print(f"🗳️ [BẦU CỬ ĐỒNG THUẬN] Phiếu của monad-02: {my_prediction}")

        # Lấy phiếu của Thủy tổ monad và Anh em monad-01
        for elder in [f"{self.owner}/monad", f"{self.owner}/monad-01"]:
            url = f"https://raw.githubusercontent.com/{elder}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url], capture_output=True)
            if res.returncode == 0:
                try:
                    data = json.loads(res.stdout.decode())
                    elder_pred = float(data.get("decision", 0.5))
                    votes.append(round(elder_pred, 4))
                    print(f"🗳️ Phiếu từ {elder}: {elder_pred}")
                except Exception: pass

        final_consensus = round(sum(votes) / len(votes), 4)
        print(f"⚖️ [KẾT QUẢ ĐỒNG THUẬN TAM GIÁC ({len(votes)} nút)]: {final_consensus}")
        return final_consensus

    # ==============================================================
    # ĐA XÚC TU HÚT GIÁC QUAN & HÚT HỒN CHỚP NHOÁNG
    # ==============================================================
    def harvest_all_tentacles(self):
        harvested = {}
        for peer in self.peers:
            target_file = f"synapse_in_{peer.replace('/', '_')}.json"
            url = f"https://raw.githubusercontent.com/{peer}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url, "-o", target_file], capture_output=True)
            if res.returncode == 0 and os.path.exists(target_file):
                try:
                    with open(target_file, "r") as f: data = json.load(f)
                    harvested[peer] = [float(x) for x in data.get("features", [0.5, 0.5])[:2]]
                    
                    # Hút hồn chớp nhoáng lưu ADN bạn bè
                    os.makedirs("synapses/harvested_memory", exist_ok=True)
                    with open(f"synapses/harvested_memory/{peer.replace('/', '_')}.json", "w") as bf:
                        json.dump(data, bf)
                        
                    for np in data.get("gossip_network", []):
                        if np not in self.peers: self.peers.append(np)
                except Exception: pass
        self.save_peers()
        return harvested

    # ==============================================================
    # VẬN HÀNH TIẾN HÓA BẤT ĐỒNG BỘ
    # ==============================================================
    def run(self):
        last_epoch = 0
        last_time = 0
        if os.path.exists(STATE_LOG):
            try:
                with open(STATE_LOG, "r") as f:
                    log = json.load(f)
                    last_epoch = log.get("generation_epoch", 0)
                    last_time = log.get("last_t", 0)
            except Exception: pass

        current_time = int(time.time())
        harvested = self.harvest_all_tentacles()

        # Bào tử ngủ đông tiết kiệm năng lượng
        if not harvested and (current_time - last_time < 3600):
            print("💤 [BÀO TỬ NGỦ ĐÔNG] Môi trường tĩnh. Đi ngủ bảo toàn năng lượng.")
            return

        current_epoch = last_epoch + 1
        print("=" * 60)
        print(f"💎 [MONAD-02] BƯỚC NHẢY TIẾN HÓA THẾ HỆ #{current_epoch} (BẬC {self.generation})")

        # 1. Gặm cỏ tri thức
        wisdom = self.autonomous_graze()
        print(f"📖 [TRI THỨC NUỐT VÀO]: \"{wisdom[:80]}...\"")
        v_wisdom = LinguisticCell.embed_text(wisdom)

        # 2. Hợp nhất qua 1+N Siêu XOR
        super_vector = []
        all_masks = {}
        for organ, signal in (harvested.items() if harvested else [("internal_wisdom", v_wisdom[:2])]):
            entangled, masks = self.swarm[0].super_xor_entangle(signal, organ)
            super_vector.extend(entangled[:2])
            all_masks[organ] = masks

        while len(super_vector) < 4: super_vector.append(0.0)
        super_vector = super_vector[:4]

        # 3. Phán quyết nội bộ
        h_outs = [cell.forward(super_vector) for cell in self.swarm]
        my_pred = self.out_cell.forward(h_outs)

        # 4. KÍCH HOẠT TAM GIÁC ĐỒNG THUẬN 3 BÊN!
        consensus_decision = self.consensus_quorum(my_pred)

        # 5. Lan truyền ngược tự sửa sai
        target = 1.0 if super_vector[0] != super_vector[1] else 0.0
        delta_out = (target - consensus_decision) * sigmoid_derivative(consensus_decision)
        deltas_h = [delta_out * self.out_cell.weights[j] * sigmoid_derivative(h_outs[j]) for j in range(NUM_CELLS)]

        self.out_cell.backward(delta_out)
        for j, cell in enumerate(self.swarm): cell.backward(deltas_h[j])

        # Đạo hàm nén gửi ngược lại dạy học
        grad_backward = [
            round(sum(deltas_h[j] * self.swarm[j].weights[0] for j in range(NUM_CELLS)), 4),
            round(sum(deltas_h[j] * self.swarm[j].weights[1] for j in range(NUM_CELLS)), 4)
        ]

        # CĂN CƯỚC CÔNG DÂN PHẢ HỆ ĐƠN TỬ VƯỢT TỔ
        node_dna = {
            "identity": self.repo_name,
            "generation": self.generation,
            "node_index": self.node_index,
            "pulse_age": self.pulse_age,
            "ancestor_root": self.ancestor_root,
            "generation_epoch": current_epoch
        }

        # 1. Phát sóng lùi: Dạy học cho thế hệ trước và giác quan
        backward_packet = {
            "contract": "bodhi.monad.v2",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "timestamp": current_time,
            "gradients_for_eye": grad_backward,
            "super_xor_masks": all_masks,
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"bwd_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }
        with open("synapse_backward.json", "w", encoding="utf-8") as f:
            json.dump(backward_packet, f, indent=4, ensure_ascii=False)

        # 2. Phát sóng tiến: Lệnh vận động mang đồng thuận tam giác
        forward_packet = {
            "contract": "bodhi.monad.v2",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "timestamp": current_time,
            "decision": consensus_decision,
            "command_pulse": [consensus_decision, round(1.0 - consensus_decision, 4)],
            "features": [consensus_decision, round(1.0 - consensus_decision, 4)],
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"fwd_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }
        with open("synapse_forward.json", "w", encoding="utf-8") as f:
            json.dump(forward_packet, f, indent=4, ensure_ascii=False)

        # 3. Nén linh hồn Ốc Mượn Hồn
        soul = {
            "node_dna": node_dna,
            "timestamp": current_time,
            "consensus": consensus_decision,
            "peers": self.peers
        }
        with open(SOUL_FILE, "w", encoding="utf-8") as f:
            json.dump(soul, f, indent=4, ensure_ascii=False)

        # 4. Ghi nhật ký thế hệ
        with open(STATE_LOG, "w") as f:
            json.dump({"generation_epoch": current_epoch, "last_t": current_time, "status": "monad02_prodigy_evolved"}, f, indent=4)

        self.save_peers()
        print(f"✨ [ĐƠN TỬ VIÊN MÃN] monad-02 đã đồng thuận tam giác và phát sóng thế hệ #{current_epoch}!")
        print("=" * 60)

if __name__ == "__main__":
    node = Monad02ProdigyEngine()
    node.run()
