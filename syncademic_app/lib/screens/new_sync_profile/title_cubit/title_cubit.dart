import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:quiver/strings.dart';

part 'title_state.dart';
part 'title_cubit.freezed.dart';

class TitleCubit extends Cubit<TitleState> {
  TitleCubit() : super(const TitleState());

  void titleChanged(String title) {
    if (isBlank(title)) {
      return emit(TitleState(title: title, error: 'Title cannot be empty'));
    }

    if (title.length > 50) {
      return emit(TitleState(title: title, error: 'Title is too long'));
    }

    emit(TitleState(title: title, error: null));
  }
}
