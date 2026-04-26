## 1 `ReportService.create_report`

### Control Flow Graph

- ![](../data/img/xxx.xxx)

### Atomic Conditions

### Structural Lower Bound

### Node Coverage

### Edge Coverage

### Condition Coverage

### Loop Coverage

### Path Coverage

### Minimal Suite Test

## 2 `MessagingService._resolve_recipient`

### Control Flow Graph

![](../../data/img/resolve_recipient.png)

### Atomic Conditions

- **C1**: `sender.role in {Role.ADMIN, Role.OPERATOR}`
- **C2a**: `message.sender` (truthy) — primo operando di `and`
- **C2b**: `message.sender.role in {Role.ADMIN, Role.OPERATOR}` — secondo operando di `and`, combinato tramite `and`
- **C3a**: `status_event.changed_by` (truthy) — primo operando di `and`
- **C3b**: `status_event.changed_by.role in {Role.ADMIN, Role.OPERATOR}` — secondo operando di `and`, combinato tramite `and`

### Structural Lower Bound

- **Nodi**: 12
- **Archi**: 16
- **Complessità ciclomatica**: V(G) = E − N + 2 = 16 − 12 + 2 = **6**
- **Nodi terminali distinti**: 4 (`return report.reporter`, `return message.sender`, `return status_event.changed_by`, `return None`)
- **Loop**: 2 (Loop 1 su `reversed(messages)`, Loop 2 su `reversed(report.status_history)`)

### Node Coverage

| Test | `sender` | `messages` | `status_history` | Outcome |
|------|----------|------------|------------------|--------------------------|
| T1 | ADMIN/OPERATOR | — | — | `return report.reporter` |
| T2 | CITIZEN | [msg con `sender` ADMIN] | — | `return message.sender` |
| T3 | CITIZEN | `[]` | [event con `changed_by` ADMIN] | `return status_event.changed_by` |
| T4 | CITIZEN | `[]` | `[]` | `return None` |

I 4 nodi terminali si trovano su percorsi mutualmente esclusivi, quindi nessun singolo test può coprirli tutti: il lower bound è **4 test**.

### Edge Coverage

| Test | `sender` | `messages` | `status_history` | Outcome |
|------|----------|------------|------------------|---------|
| T1 | ADMIN/OPERATOR | — | — | `return report.reporter` |
| T2 | CITIZEN | [msg con `sender` ADMIN] | — | `return message.sender` |
| T3 | CITIZEN | `[]` | [event con `changed_by` ADMIN] | `return status_event.changed_by` |
| T5 | CITIZEN | [msg con `sender` non-ADMIN] | [event con `changed_by` non-ADMIN] | `return None` |

I back-edge dei loop (iterazione senza match) non sono coperti dalla suite di node coverage: T4 viene sostituito da T5, che forza entrambe le iterazioni senza match. Il lower bound rimane **4 test**.

### Condition Coverage

| Test | `sender` | `messages` | `status_history` | Outcome |
|------|----------|------------|------------------|---------|
| T1 | ADMIN/OPERATOR | — | — | `return report.reporter` |
| T2 | CITIZEN | [msg con `sender` ADMIN] | — | `return message.sender` |
| T3 | CITIZEN | `[]` | [event con `changed_by` ADMIN] | `return status_event.changed_by` |
| T5 | CITIZEN | [msg con `sender` non-ADMIN] | [event con `changed_by` non-ADMIN] | `return None` |
| T6 | CITIZEN | [msg con `sender=None`] | [event con `changed_by=None`] | `return None` |

| Condizione | Testimone True | Testimone False |
|------------|----------------|-----------------|
| C1 | T1 | T2, T3, T5, T6 |
| C2a | T2, T5 | T6 |
| C2b | T2 | T5 |
| C3a | T3, T5 | T6 |
| C3b | T3 | T5 |

C2 e C3 contengono ciascuna un `and` composto, rendendo lo short-circuit rilevante: C2b è valutata solo se C2a=True; C3b solo se C3a=True. Coprire C2a=False e C3a=False richiede un test aggiuntivo T6 non presente nelle suite precedenti. Il lower bound è **5 test** in entrambe le convenzioni.

### Loop Coverage

| Test | `messages` | `status_history` | Loop 1 (iterazioni) | Loop 2 (iterazioni) |
|------|------------|------------------|---------------------|---------------------|
| T4 | `[]` | `[]` | 0 | 0 |
| T2 | [1 msg, `sender` ADMIN] | — | 1 (early return) | — |
| T3 | `[]` | [1 event, `changed_by` ADMIN] | 0 | 1 (early return) |
| T5 | [1 msg, `sender` non-ADMIN] | [1 event, `changed_by` non-ADMIN] | 1 (esausto) | 1 (esausto) |
| T7 | [2 msg, `sender` non-ADMIN] | [2 event, `changed_by` non-ADMIN] | 2+ | 2+ |

Loop 2 è raggiungibile solo quando Loop 1 si esaurisce senza match: i test con 2+ iterazioni devono quindi usare messaggi e status event senza ruolo ADMIN/OPERATOR. T7 è il solo test aggiuntivo rispetto alle suite precedenti. Il lower bound è **5 test**.

### Path Coverage

| ID | Percorso | Outcome |
|----|----------|---------|
| P1 | C1=True | `return report.reporter` |
| P2 | C1=False, Loop1=0, Loop2=0 | `return None` |
| P3 | C1=False, Loop1 trova match | `return message.sender` |
| P4 | C1=False, Loop1 esausto, Loop2 trova match | `return status_event.changed_by` |
| P5 | C1=False, Loop1 esausto, Loop2 esausto | `return None` |

| Test | `sender` | `messages` | `status_history` | Percorso coperto |
|------|----------|------------|------------------|-----------------|
| T1 | ADMIN/OPERATOR | — | — | P1 |
| T4 | CITIZEN | `[]` | `[]` | P2 |
| T2 | CITIZEN | [1 msg, `sender` ADMIN] | — | P3 |
| T3 | CITIZEN | `[]` | [1 event, `changed_by` ADMIN] | P4 |
| T5 | CITIZEN | [1 msg, `sender` non-ADMIN] | [1 event, `changed_by` non-ADMIN] | P5 |

La presenza dei loop rende i percorsi teoricamente infiniti; considerando ogni loop come blocco 0/≥1 iterazioni si ottengono 5 percorsi strutturalmente distinti. Il lower bound è **5 test**.

### Minimal Suite Test

| Test | `sender` | `messages` | `status_history` | Outcome | Criteri coperti |
|------|----------|------------|------------------|---------|-----------------|
| T1 | ADMIN/OPERATOR | — | — | `return report.reporter` | Node, Edge, Condition (C1=T), Path (P1) |
| T2 | CITIZEN | [1 msg, `sender` ADMIN] | — | `return message.sender` | Node, Edge, Condition (C2a=T, C2b=T), Path (P3), Loop (L1=1) |
| T3 | CITIZEN | `[]` | [1 event, `changed_by` ADMIN] | `return status_event.changed_by` | Node, Edge, Condition (C3a=T, C3b=T), Path (P4), Loop (L1=0, L2=1) |
| T4 | CITIZEN | `[]` | `[]` | `return None` | Node, Path (P2), Loop (L2=0) |
| T5 | CITIZEN | [1 msg, `sender` non-ADMIN] | [1 event, `changed_by` non-ADMIN] | `return None` | Edge (back-edge L1/L2), Condition (C2b=F, C3b=F), Path (P5), Loop (L1=1 esausto, L2=1 esausto) |
| T6 | CITIZEN | [1 msg, `sender=None`] | [1 event, `changed_by=None`] | `return None` | Condition (C2a=F, C3a=F) |
| T7 | CITIZEN | [2 msg, `sender` non-ADMIN] | [2 event, `changed_by` non-ADMIN] | `return None` | Loop (L1=2+, L2=2+) |

| Criterio | Test minimi | Test utilizzati |
|----------|:-----------:|-----------------|
| Node coverage | 4 | T1, T2, T3, T4 |
| Edge coverage | 4 | T1, T2, T3, T5 |
| Condition coverage | 5 | T1, T2, T3, T5, T6 |
| Path coverage | 5 | T1, T2, T3, T4, T5 |
| Loop coverage | 5 | T2, T3, T4, T5, T7 |
| **Suite completa** | **7** | **T1–T7** |

## 3 `NotificationService.notify_status_change`

### Control Flow Graph

- ![](../data/img/xxx.xxx)

### Atomic Conditions

### Structural Lower Bound

### Node Coverage

### Edge Coverage

### Condition Coverage

### Loop Coverage

### Path Coverage

### Minimal Suite Test


## 4 `NotificationService.count_unread_message_notifications_by_report`

### Control Flow Graph

- ![](../data/img/xxx.xxx)

### Atomic Conditions

### Structural Lower Bound

### Node Coverage

### Edge Coverage

### Condition Coverage

### Loop Coverage

### Path Coverage

### Minimal Suite Test


## 5 `UserService.update_user`

### Control Flow Graph

- ![](../data/img/xxx.xxx)

### Atomic Conditions

### Structural Lower Bound

### Node Coverage

### Edge Coverage

### Condition Coverage

### Loop Coverage

### Path Coverage

### Minimal Suite Test

