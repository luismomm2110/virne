graph [
  node_attrs_setting "_networkx_list_start"
  node_attrs_setting [
    name "cpu"
    type "resource"
    owner "node"
    distribution "uniform"
    dtype "int"
    generative "True"
    low "10"
    high "40"
  ]
  link_attrs_setting "_networkx_list_start"
  link_attrs_setting [
    name "bw"
    type "resource"
    owner "link"
    distribution "uniform"
    dtype "int"
    generative "True"
    low "20"
    high "80"
  ]
  topology___type "random"
  topology___random_prob "0.5"
  output___save_dir "dataset/v_nets"
  output___v_nets_save_dir "v_nets"
  output___v_nets_file_name "v_net.gml"
  output___events_file_name "events.yaml"
  output___setting_file_name "v_sim_setting.yaml"
  id 184
  arrival_time 3692.0
  lifetime 172.14893206224505
  node [
    id 0
    label "0"
    cpu 40
  ]
  node [
    id 1
    label "1"
    cpu 27
  ]
  node [
    id 2
    label "2"
    cpu 20
  ]
  node [
    id 3
    label "3"
    cpu 28
  ]
  node [
    id 4
    label "4"
    cpu 37
  ]
  node [
    id 5
    label "5"
    cpu 34
  ]
  edge [
    source 0
    target 4
    bw 21
  ]
  edge [
    source 1
    target 2
    bw 80
  ]
  edge [
    source 1
    target 4
    bw 70
  ]
  edge [
    source 2
    target 3
    bw 59
  ]
  edge [
    source 2
    target 4
    bw 50
  ]
  edge [
    source 2
    target 5
    bw 66
  ]
  edge [
    source 3
    target 4
    bw 73
  ]
  edge [
    source 3
    target 5
    bw 37
  ]
  edge [
    source 4
    target 5
    bw 24
  ]
]
