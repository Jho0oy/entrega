#!/usr/bin/env bash
# Testes de aceitação do buscador.sh contra dados simulados (sem acessar o TSE).
# Uso: tests/run_tests.sh
set -Eeuo pipefail
cd "$(dirname "$0")/.."
PORT=8799
FIX="$(mktemp -d)"
python3 -I tests/make_fixtures.py "$FIX"
(cd "$FIX" && python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1) &
SRV=$!
trap 'kill $SRV 2>/dev/null; rm -rf "$FIX"' EXIT
sleep 1
export TSE_RESULTS_BASE_URL="http://127.0.0.1:$PORT" TSE_RESULTS_COLOR=never

pass=0; fail=0
report() { # descrição, status (0 = ok)
  if (($2 == 0)); then printf 'OK    %s\n' "$1"; pass=$((pass+1))
  else printf 'FALHA %s\n' "$1"; fail=$((fail+1)); fi
}
out() { ./buscador.sh "$@" 2>/dev/null || true; }
has()   { local o; o="$(out "${@:2}")"; grep -q -- "$1" <<<"$o"; }   # has PADRÃO args...
hasnt() { ! has "$@"; }
count() { local o; o="$(out "${@:2}")"; grep -c -- "$1" <<<"$o" || true; }   # count PADRÃO args...
fails() { ! ./buscador.sh "$@" >/dev/null 2>&1; }

report "lista todos os municípios da UF"              $([[ $(./buscador.sh --listar-municipios | wc -l) -eq 3 ]]; echo $?)
report "1º turno traz todos os municípios"            $([[ $(count '(.....) - 1º turno') -eq 3 ]]; echo $?)
report "2º turno só traz cargos com 2º turno"         $(hasnt 'Deputado' -t 2; echo $?)
report "turnos aparecem separados (todos)"            $([[ $(count 'TURNO - Eleições' -t todos) -eq 2 ]]; echo $?)
report "eleito marcado (Governador, 1º turno)"        $(has 'GOVERNADOR X.*ELEITO' -c 3 -m 07242; echo $?)
report "Presidente sem eleito no 1º turno"            $(hasnt 'CANDIDATO A.*ELEITO' -c 1; echo $?)
report "Presidente eleito no 2º turno"                $(has 'CANDIDATO A.*ELEITO' -t 2 -c 1; echo $?)
report "Governador sem 2º turno não quebra"           $(has 'cargo 3. sem dados no 2º turno' -t 2; echo $?)
report "Senador com 2 eleitos"                        $([[ $(count ELEITO -c 5 -m 07242) -ge 4 ]]; echo $?)
report "--somente-eleitos oculta não eleitos"         $(hasnt 'GOVERNADOR Y' -c 3 -m 07242 -e; echo $?)
report "filtro por nome com acento"                   $(has 'SÃO LUÍS (08850)' -m 'são luís' -c 3; echo $?)
report "filtro por código de município"               $([[ $(count '(.....) - 1º turno' -m 07242) -eq 1 ]]; echo $?)
report "município sem arquivo não derruba o script"   $(has 'sem dados para este município' -c 7; echo $?)
report "limite respeitado"                            $(hasnt 'SENADOR TRES' -c 5 -m 07242 -l 2; echo $?)
report "limite maior mostra o 3º candidato"           $(has 'SENADOR TRES' -c 5 -m 07242 -l 3; echo $?)
report "erro: turno inválido"                         $(fails -t 3; echo $?)
report "erro: cargo inválido"                         $(fails -c 9; echo $?)
report "erro: município com 3 dígitos"                $(fails -m 123; echo $?)
report "erro: opção sem valor"                        $(fails -t; echo $?)
report "erro: servidor indisponível"                  $(TSE_RESULTS_BASE_URL=http://127.0.0.1:1 fails -m 07242; echo $?)
report "sem ANSI quando cor=never"                    $(hasnt $'\033' ; echo $?)
printf '\n%d ok, %d falha(s)\n' "$pass" "$fail"
((fail == 0))
