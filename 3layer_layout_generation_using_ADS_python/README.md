# RFPro FEM Automation for 3-Metal Layer Stripline

This project provides a suite of Python scripts to automate the entire workflow from design to RFPro EM simulation for a 3-metal layer stripline structure using the **ADS 2025 Update2_1** Python API[cite: 9, 26].

## 🛠 Environment & Requirements
* **Software**: Keysight Advanced Design System (ADS) 2025 Update 2_1[cite: 9].
* **Language**: Python (ADS Python PDE API)[cite: 22].
* **IDE**: Integrated for Visual Studio[cite: 26].

## 📋 Key Features & Workflow
The automation follows a structured sequence as defined in the project flowchart[cite: 13]:

1.  **Workspace Creation**: Initializes a new ADS workspace[cite: 14].
2.  **Add Library**: Automatically links required design libraries[cite: 15].
3.  **Layout Generation**: Constructs a customized 3-layer metal layout[cite: 16].
4.  **Create Tech**: Generates the necessary technology information for the design[cite: 17].
5.  **Define Substrate**: Configures the stack-up and substrate properties[cite: 18].
6.  **RFPro EM Setup**: Configures EM analysis settings for FEM or Momentum[cite: 19].
7.  **EM Simulation**: Executes the simulation engine[cite: 20].
8.  **Result Export**: S-parameter export and plotting (To be implemented in the next phase)[cite: 21, 27].

---

## 📂 File Structure
Descriptions of the core Python scripts included in this repository:

| Filename | Description |
| :--- | :--- |
| `Top_wrk_creation_3layer.py` | Main wrapper script for environment setup and procedure execution[cite: 1, 2]. |
| `drawing_layout.py` | Handles tech generation and layout creation for the 3-layer stripline[cite: 3, 4]. |
| `create_subst.py` | Manages the substrate creation process[cite: 5, 6]. |
| `create_rfpro_view.py` | Generates the RFPro view based on the created layout[cite: 7, 8]. |
| `RFPro_EM_Setup_ads2025u2.py` | Detailed EM setup for RFPro (FEM/Momentum configurations)[cite: 9, 10]. |

---

## 📐 Design Specifications
The project focuses on a 2-substrate, 3-metal layer stripline with a customized shape as requested[cite: 24, 25].

* **Stack-up Details**:
    * **AIR**: Top layer[cite: 11].
    * **em_Sub (9.6)**: 138 micron thickness[cite: 11].
    * **Alumina (9.6)**: 200 micron thickness[cite: 11].
    * **em_Sub (9.6)**: 156 (138+18) micron thickness[cite: 11].
* **Simulation Performance**:
    * Validated S-parameter results ($S_{11}$, $S_{22}$) at 3.333 GHz[cite: 12].
    * Magnitude analysis performed over a 0 to 10 GHz frequency range[cite: 12].

---

## 📝 Notes
* The workspace creation code was generated using API design environment help and existing usage cases[cite: 26].
* For full automation, the 'S-parameter import and plotting' code block will be added in the next development step[cite: 27].
