class PropertyLawDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para ver, editar o eliminar una PropertyLaw específica de una propiedad"""
    serializer_class = PropertyLawSerializer
    
    def get_queryset(self):
        """Filtrar PropertyLaws por la propiedad especificada"""
        property_id = self.kwargs.get('property_id')
        return PropertyLaw.objects.filter(property_id=property_id)
    
    def get_object(self):
        """Obtener la PropertyLaw específica"""
        law_id = self.kwargs.get('law_id')
        return get_object_or_404(self.get_queryset(), pk=law_id)
    
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle de una PropertyLaw"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Actualizar una PropertyLaw"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Mapear 'media' a 'url' si viene con ese nombre
        data = request.data.copy()
        if 'media' in request.FILES and 'url' not in request.FILES:
            data['url'] = request.FILES['media']
        
        serializer = PropertyLawCreateSerializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            response_serializer = PropertyLawSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar una PropertyLaw"""
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'PropertyLaw eliminada exitosamente'}, status=status.HTTP_204_NO_CONTENT)
