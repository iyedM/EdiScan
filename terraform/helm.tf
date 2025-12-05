resource "helm_release" "nginx_ingress" {
  name             = "nginx-ingress"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  version          = "4.8.3"

  set {
    name  = "controller.service.loadBalancerIP"
    value = google_compute_global_address.ingress_ip.address
  }

  depends_on = [google_container_node_pool.primary_nodes]
}

resource "helm_release" "cert_manager" {
  name             = "cert-manager"
  repository       = "https://charts.jetstack.io"
  chart            = "cert-manager"
  namespace        = "cert-manager"
  create_namespace = true
  version          = "1.13.2"

  set {
    name  = "installCRDs"
    value = "true"
  }

  depends_on = [google_container_node_pool.primary_nodes]
}

resource "helm_release" "ediscan" {
  name             = "ediscan"
  chart            = "../helm/ediscan"
  namespace        = "ediscan"
  create_namespace = true

  set {
    name  = "image.repository"
    value = split(":", var.docker_image)[0]
  }

  set {
    name  = "image.tag"
    value = split(":", var.docker_image)[1]
  }

  set {
    name  = "ingress.hosts[0].host"
    value = var.domain
  }

  set {
    name  = "ingress.tls[0].hosts[0]"
    value = var.domain
  }

  depends_on = [
    helm_release.nginx_ingress,
    helm_release.cert_manager
  ]
}

