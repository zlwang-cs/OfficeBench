

# OfficeBench: Evaluar agentes de lenguaje en múltiples aplicaciones para la automatización de oficina

🖋 **Autores:** [Zilong Wang](https://zilongwang.me), Yuedong Cui, [Li Zhong](https://github.com/FloridSleeves), Zimin Zhang, [Da Yin](https://wadeyin9712.github.io/), [Bill Yuchen Lin](https://yuchenlin.xyz/), [Jingbo Shang](https://shangjingbo1226.github.io/)

Presentamos **OfficeBench**, uno de los primeros benchmarks de automatización de oficina para evaluar la capacidad de los agentes LLM actuales para abordar tareas de oficina en flujos de trabajo realistas. **OfficeBench** requiere que los agentes LLM realicen planificación a largo plazo viable, cambien con destreza entre aplicaciones de manera oportuna y fundamenten con precisión sus acciones dentro de un amplio espacio de acción combinado grande, basándose en las demandas contextuales del flujo de trabajo.

<p align="center">
<img src=assets/officebench.jpg width=900/>
</p>

**OfficeBench es uno de los primeros benchmarks de automatización de oficina para agentes de lenguaje.** Evaluamos la capacidad de los agentes de lenguaje para realizar flujos de trabajo de oficina complejos en múltiples aplicaciones utilizando métodos de evaluación personalizados, como Coincidencia Exacta, Coincidencia Difusa y Evaluación basada en Ejecución.

## 🧩 Arquitectura

<p align="center">
<img src=assets/architecture.jpg width=900/>
</p>

El agente LLM aprovecha las operaciones de múltiples aplicaciones para construir una cadena de operaciones que aborda eficazmente las tareas de oficina. **El marco se formula como un sistema de transición donde la aplicación actual _actúa_ como el _estado_ y las operaciones _actúan_ como las _transiciones_.** Operaciones especializadas, como `read_file` y `send_email`, realizan tareas específicas.

## 📈 Tabla de Clasificación
*`X App(s)` indica la cantidad de aplicaciones que requiere la tarea. `(X)` indica la cantidad de tareas en esta categoría.*

| Agentes LLM                                | 1 App (93) | 2 Apps (95) | 3 Apps (112) | Total (300) |
| ----------------------------------------- | --------------- | ------------- | ---------------- | ------------- |
| **Modelos Propietarios**                    |                 |               |                  |               |
| Gemni-1.0 Pro (Feb 2024)                  | 24.73           | 13.68         | 0.89             | 12.33         |
| Gemni-1.5 Flash (May 2024)                | 34.41           | 24.21         | 0.89             | 18.67         |
| Gemni-1.5 Pro (May 2024)                  | 41.94           | 32.63         | 7.14             | 26.00         |
| GPT-3.5 Turbo (0125)                      | 8.60            | 7.45          | 0.89             | 5.35          |
| GPT-4 Turbo (2024-04-09)                  | 56.99           | 50.63         | 11.61            | 38.00         |
| GPT-4 Omni (2024-05-13)                   | 64.52           | 60.00         | 21.43            | 47.00         |
| **Modelos Open-weights**                   |                 |               |                  |               |
| Llama 3 (70B-Instruct)                    | 39.79           | 41.05         | 5.36             | 27.33         |
| Qwen 2 (72B-Instruct)                     | 30.23           | 28.42         | 8.04             | 21.16         |

*(Nota: Esta tabla de clasificación se actualizará continuamente a medida que se disponga de nuevos datos y actualizaciones de modelos.)*

## 🛠️ Configuración

```
conda create -n officebench python=3.10
conda activate officebench
pip install -r requirements.txt
```

## 🤖 Ejecutar Agente LLM

```shell
# Prepara tu clave de OpenAI en openai_key.txt si llamas a modelos de OpenAI.
# Prepara tu clave de Gemini en gemini_key.txt si llamas a modelos de Gemini.
# Inicia un servidor vLLM si llamas a modelos de Huggingface.
# Consulta `generate_command.ipynb` para generar tus comandos personalizados fácilmente.

python agent_interact.py \
--docker_name {docker_name} \         # nombre de la imagen de docker: ej. officebench
--container_name {container_name} \   # nombre del contenedor: ej. officebench-test
--model_name {model_name} \           # ahora soporta OpenAI/Gemini/vLLM (ver abajo)
--task_dir {task_dir} \               # directorio de tareas: ej. 'tasks/1-20'
--config_file {config_file} \         # archivo de configuración: ej. 'tasks/1-20/subtasks/0.json'
--tag {tag} \                         # una etiqueta única para tu ejecución actual: ej. July24-test
--max_iter {max_iter} \               # número máximo de iteraciones: ej. 20
--mode {mode}                         # modo de ejecución: default/force_new/use_llm_cache (ver abajo)
```

### LLMs Compatibles

- **OpenAI:** Para utilizar la API de OpenAI con modelos de lenguaje específicos, simplemente especifica el [nombre del modelo](https://platform.openai.com/docs/models), como `gpt-4-turbo`.
- **Gemini:** Al igual que la API de OpenAI, puedes especificar [modelos de Gemini](https://ai.google.dev/gemini-api/docs/models/gemini) por nombre, por ejemplo, `gemini-1.5-pro`.
- **vLLM:** Para utilizar LLMs de [Huggingface](https://huggingface.co/models) como base, debes iniciar un [Servidor Compatible con OpenAI](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) desde vLLM.

### Modo de Ejecución

- **default**: Opera sin caché ni sobrescritura. Genera un error si los resultados ya existen.
- **force_new**: Sobrescribe los resultados existentes si se encuentran.
- **use_llm_cache**: Carga el historial de chat anterior del LLM y continúa el procesamiento de tareas. Útil para ampliar `max_iter` después de los experimentos iniciales.

### Nomenclatura de las Tareas

Las tareas anotadas se pueden encontrar en `tasks/{app_num}-{task_id}/subtask/{subtask_id}.json`, que incluye la *descripción de la tarea* y los *métodos de evaluación*.

## ✅ Evaluación

```shell
python evaluation.py \
--model_name {model_name} \           # el LLM que utilizaste (`--model_name` usado en agent_interact.py)
--tag_name {tag_name} \               # la etiqueta que utilizaste (`--tag` usado en agent_interact.py)
```

Los resultados finales se escribirán en `results/{model_name}_{tag_name}_result.jsonl`

## ❤️ Agradecimientos

Agradecemos enormemente a [InterCode](https://github.com/princeton-nlp/intercode) por proporcionar el fantástico framework de agentes. También agradecemos sinceramente a los colaboradores del equipo de vLLM por proporcionar el [Servidor Compatible con OpenAI](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) para llamar fácilmente a LLMs de código abierto.
